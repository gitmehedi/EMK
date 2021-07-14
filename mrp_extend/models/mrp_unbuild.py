# imports of python
import datetime

# imports of odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    def _get_default_location_id(self):
        location = False
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(
                self.env.context['default_picking_type_id']).default_location_src_id
        if not location:
            location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
        return location and location.id or False

    def _get_default_location_dest_id(self):
        location = False
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(
                self.env.context['default_picking_type_id']).default_location_dest_id
        if not location:
            location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
        return location and location.id or False

    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id

    mo_id = fields.Many2one('mrp.production', domain="[('product_id', '=', product_id), ('state', '=', 'done')]")
    state = fields.Selection(selection_add=[('cancel', 'Cancelled')], track_visibility='onchange')
    date_unbuild = fields.Date(string='Date', copy=False, states={'done': [('readonly', True)]})
    has_moves = fields.Boolean(compute='_compute_has_moves')
    location_id = fields.Many2one('stock.location', 'Location', default=_get_default_location_id, required=True, states={'done': [('readonly', True)]})
    location_dest_id = fields.Many2one('stock.location', 'Destination Location', default=_get_default_location_dest_id, required=True, states={'done': [('readonly', True)]})
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', default=_get_default_picking_type, required=True)

    @api.multi
    @api.depends('produce_line_ids')
    def _compute_has_moves(self):
        for unbuild in self:
            unbuild.has_moves = any(unbuild.produce_line_ids)

    @api.onchange('mo_id')
    def onchange_mo_id(self):
        super(MrpUnbuild, self).onchange_mo_id()
        if self.mo_id:
            self.date_unbuild = self.mo_id.date_planned_start
            self.bom_id = self.mo_id.bom_id

        if not self.mo_id:
            self.bom_id = self.env['mrp.bom']._bom_find(product=self.product_id)
            self.product_qty = False
            self.date_unbuild = datetime.datetime.today()

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(MrpUnbuild, self).onchange_product_id()
        if self.mo_id:
            self.mo_id = False
            self.product_qty = False
            self.date_unbuild = False

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        location = self.env.ref('stock.stock_location_stock')
        self.location_id = self.picking_type_id.default_location_src_id.id or location.id
        self.location_dest_id = self.picking_type_id.default_location_dest_id.id or location.id

    @api.constrains('date_unbuild')
    def _check_date_unbuild(self):
        if self.date_unbuild > datetime.datetime.today().strftime('%Y-%m-%d'):
            raise ValidationError(_("Date cannot be greater than Current Date!!"))

    @api.model
    def create(self, vals):
        if vals.get('mo_id', False):
            mo = self.env['mrp.production'].search([('id', '=', vals['mo_id'])])
            vals['date_unbuild'] = mo.date_planned_start

        if vals.get('product_id', False):
            product = self.env['product.product'].search([('id', '=', vals['product_id'])])
            vals['product_uom_id'] = product.uom_id.id

        unbuild = super(MrpUnbuild, self).create(vals)

        consume_move = unbuild._generate_consume_moves()
        produce_moves = unbuild._generate_produce_moves()

        return unbuild

    @api.multi
    def unlink(self):
        if any(rec.state == 'done' for rec in self):
            raise UserError(_("You can not delete Unbuild Orders that are in done state."))

        return super(MrpUnbuild, self).unlink()

    @api.multi
    def action_cancel(self):
        if any(unbuild.state == 'done' for unbuild in self):
            raise UserError(_("You can not cancel Unbuild Order that is in done state."))

        for unbuild in self:
            consume_moves = unbuild.consume_line_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            produce_moves = unbuild.produce_line_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            (consume_moves | produce_moves).action_cancel()

        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_unbuild(self):
        self.ensure_one()
        if self.product_id.tracking != 'none' and not self.lot_id.id:
            raise UserError(_('Should have a lot for the finished product'))

        consume_move = self.consume_line_ids[0]
        produce_moves = self.produce_line_ids

        # Search quants that passed production order
        qty = self.product_qty  # Convert to qty on product UoM
        if self.mo_id:
            finished_moves = self.mo_id.move_finished_ids.filtered(
                lambda move: move.product_id == self.mo_id.product_id)
            domain = [('qty', '>', 0), ('history_ids', 'in', finished_moves.ids)]
        else:
            domain = [('qty', '>', 0)]
        quants = self.env['stock.quant'].quants_get_preferred_domain(
            qty, consume_move,
            domain=domain,
            preferred_domain_list=[],
            lot_id=self.lot_id.id)
        self.env['stock.quant'].quants_reserve(quants, consume_move)

        if consume_move.has_tracking != 'none':
            if not quants[0][0]:
                raise UserError(_("You don't have in the stock the lot %s.") % (self.lot_id.name,))
            self.env['stock.move.lots'].create({
                'move_id': consume_move.id,
                'lot_id': self.lot_id.id,
                'quantity_done': consume_move.product_uom_qty,
                'quantity': consume_move.product_uom_qty})
        else:
            consume_move.quantity_done = consume_move.product_uom_qty
        consume_move.move_validate()
        original_quants = consume_move.quant_ids.mapped('consumed_quant_ids')

        for produce_move in produce_moves:
            if produce_move.has_tracking != 'none':
                original = original_quants.filtered(lambda quant: quant.product_id == produce_move.product_id)
                if not original:
                    raise UserError(_("You don't have in the stock the required lot/serial number for %s .") % (
                    produce_move.product_id.name,))
                quantity_todo = produce_move.product_qty
                for quant in original:
                    if quantity_todo <= 0:
                        break
                    move_quantity = min(quantity_todo, quant.qty)
                    self.env['stock.move.lots'].create({
                        'move_id': produce_move.id,
                        'lot_id': quant.lot_id.id,
                        'quantity_done': produce_move.product_id.uom_id._compute_quantity(move_quantity,
                                                                                          produce_move.product_uom),
                        'quantity': produce_move.product_id.uom_id._compute_quantity(move_quantity,
                                                                                     produce_move.product_uom),
                    })
                    quantity_todo -= move_quantity
            else:
                produce_move.quantity_done = produce_move.product_uom_qty
        produce_moves.move_validate()
        produced_quant_ids = produce_moves.mapped('quant_ids').filtered(lambda quant: quant.qty > 0)
        consume_move.quant_ids.sudo().write({'produced_quant_ids': [(6, 0, produced_quant_ids.ids)]})

        # cancel stock move which are not in done or cancel state
        moves_to_cancel = (self.consume_line_ids | self.produce_line_ids).filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_to_cancel.action_cancel()

        return self.write({'state': 'done'})

    def _generate_consume_moves(self):
        moves = super(MrpUnbuild, self)._generate_consume_moves()
        moves.write({'date': self.date_unbuild, 'date_expected': self.date_unbuild})

        return moves

    def _generate_move_from_bom_line(self, bom_line, quantity):
        move = super(MrpUnbuild, self)._generate_move_from_bom_line(bom_line, quantity)
        price_unit = self.mo_id.move_raw_ids.filtered(lambda x: x.product_id.id == bom_line.product_id.id).price_unit or bom_line.product_id.standard_price
        move.write({'date': self.date_unbuild, 'date_expected': self.date_unbuild, 'price_unit': price_unit})
        move.action_confirm()

        return move
