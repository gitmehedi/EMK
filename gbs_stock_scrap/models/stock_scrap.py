# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import time
import datetime
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class GBSStockScrap(models.Model):
    _name = 'gbs.stock.scrap'
    _description = 'GBS Stock Scrap'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    def _get_default_scrap_location_id(self):
        return self.env['stock.location'].search([('scrap_location', '=', True)], limit=1).id

    def _get_default_location_id(self):
        return self.env['stock.location'].search([('operating_unit_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id

    name = fields.Char('Reference',  default=lambda self: _('New'),copy=False,
                       readonly=True, required=True,
                       states={'draft': [('readonly', False)]})
    reason = fields.Text('Reason',readonly=True, required=True,
                         states={'draft': [('readonly', False)]})
    request_by = fields.Many2one('res.users', string='Request By', required=True, readonly=True,
                                 default=lambda self: self.env.user)
    requested_date = fields.Datetime('Request Date', required=True, default=fields.Datetime.now)
    approved_date = fields.Datetime('Approved Date', readonly=True)
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True,
                                  help="who have approve or reject.")
    location_id = fields.Many2one('stock.location', 'Location',default=_get_default_location_id,
                                  domain="[('usage', '=', 'internal'),('operating_unit_id', '=',operating_unit_id)]",required=True,
                                  states={'draft': [('readonly', False)]})
    scrap_location_id = fields.Many2one('stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
                                        domain="[('scrap_location', '=', True)]", readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    picking_id = fields.Many2one('stock.picking', 'Picking', states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type',
                                      compute='_computePickingType',store=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    package_id = fields.Many2one('stock.quant.package', 'Package')
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    product_lines = fields.One2many('gbs.stock.scrap.line', 'stock_scrap_id', 'Products', readonly=True,
                                    states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True, copy=False, track_visibility='onchange', default='draft')

    ####################################################
    # Business methods
    ####################################################

    @api.multi
    @api.depends('location_id')
    def _computePickingType(self):
        for scrap in self:
            picking_type_obj = scrap.env['stock.picking.type']
            picking_type_ids = picking_type_obj.search(
                ['&',('default_location_src_id', '=', scrap.location_id.id),
                 ('code', '=', 'internal')])
            picking_type_id = picking_type_ids and picking_type_ids[0] or False
            scrap.picking_type_id = picking_type_id

    @api.multi
    def scrap_confirm(self):
        for scrap in self:
            if not scrap.product_lines:
                raise UserError(_('You cannot confirm which has no line.'))

            res = {
                'state': 'waiting_approval'
            }
            new_seq = self.env['ir.sequence'].next_by_code('stock.scraping')
            if new_seq:
                res['name'] = new_seq

            scrap.write(res)

    @api.multi
    def scrap_approve(self):
        res = {
            'state': 'approved',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        for scrap in self:
            scrap.action_picking_create()
        self.write(res)

    @api.one
    def action_picking_create(self):
        move_obj = self.env['stock.move']
        picking_id = False
        if self.product_lines:
            picking_id = self._create_pickings_and_procurements()
        move_ids = move_obj.search([('picking_id', '=', picking_id)])
        self.write({'picking_id': picking_id,})

    def _get_origin_moves(self):
        return self.picking_id and self.picking_id.move_lines.filtered(lambda x: x.product_id == self.product_id)

    @api.model
    def _create_pickings_and_procurements(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        need_purchase_req = False
        picking_id = False
        for line in self.product_lines:
            date_planned = datetime.datetime.strptime(self.requested_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    vals = self._prepare_indent_picking()
                    picking = picking_obj.create(vals)
                    if picking:
                        picking_id = picking.id
                moves = self._get_origin_moves() or self.env['stock.move']
                move=move_obj.create(self._prepare_indent_line_move(line, picking_id, date_planned))
                quants = self.env['stock.quant'].quants_get_preferred_domain(
                    move.product_qty, move,
                    domain=[
                        ('qty', '>', 0),
                        ('lot_id', '=', self.lot_id.id),
                        ('package_id', '=', self.package_id.id)])
                if any([not x[0] for x in quants]):
                    # if line.product_uom_qty > line.qty_available:
                    raise UserError(_(
                        'You cannot scrap a move without having available stock for %s. You can correct it with an inventory adjustment.') % line.product_id.name)
                self.env['stock.quant'].quants_reserve(quants, move)
                move.action_done()
                self.write({'move_id': move.id})
                moves.recalculate_move_state()
        return picking_id

    def _prepare_indent_picking(self):
        pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
        res = {
            'invoice_state': 'none',
            'picking_type_id': self.picking_type_id.id,
            'name': pick_name,
            'origin': self.name,
            'date': self.requested_date,
            'partner_id': self.request_by.partner_id.id or False,
            'location_id': self.location_id.id,
            'location_dest_id': self.scrap_location_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            # 'priority': self.requirement,
            # 'type': 'internal',
            # 'move_type': self.move_type,
        }
        if self.company_id:
            res = dict(res, company_id=self.company_id.id)
        return res

    def _prepare_indent_line_move(self, line, picking_id, date_planned):
        location_id = self.location_id.id

        res = {
            'name': self.name,
            'origin': self.name or self.picking_id.name,
            'location_id': location_id,
            'scrapped': True,
            'location_dest_id': self.scrap_location_id.id,
            'picking_id': picking_id or False,
            'product_id': line.product_id.id,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'date': date_planned,
            'date_expected': date_planned,
            'picking_type_id': self.picking_type_id.id,

        }

        if line.product_id.type in ('service'):
            if not line.original_product_id:
                raise models.except_osv(_("Warning !"),
                                        _("You must define material or parts that you are going to repair !"))

            upd_res = {
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
            }
            res.update(upd_res)

        return res

    @api.multi
    def scrap_reject(self):
        res = {
            'state': 'reject',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)

    @api.multi
    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', '=', self.picking_id.id)]
        return action

    @api.multi
    def action_get_stock_move(self):
        action = self.env.ref('stock.stock_move_action').read([])[0]
        action['domain'] = [('id', '=', self.move_id.id)]
        return action

    ####################################################
    # ORM Overrides methods
    ####################################################

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete this !!'))
        return super(GBSStockScrap, self).unlink()

class GBSStockScrapLines(models.Model):
    _name = 'gbs.stock.scrap.line'
    _description = 'GBS Stock Scrap Line'
    _order = 'id desc'

    stock_scrap_id = fields.Many2one('gbs.stock.scrap', string='Stock Scrap', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    qty_available = fields.Float('In Stock', compute='_computeProductQuentity', store=True)
    name = fields.Text('Specification', store=True)
    sequence = fields.Integer('Sequence')

    ####################################################
    # Business methods
    ####################################################
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {'value': {'product_uom_qty': 1.0,
                              'product_uom': False,
                              'qty_available': 0.0,
                              'name': '',
                              }
                    }
        product_obj = self.env['product.product']
        product = product_obj.search([('id', '=', self.product_id.id)])
        product_name = product.name_get()[0][1]
        self.name = product_name
        self.product_uom = product.uom_id.id

    @api.depends('product_id')
    @api.multi
    def _computeProductQuentity(self):
        for productLine in self:
            if productLine.product_id.id:
                location_id = productLine.stock_scrap_id.location_id.id
                product_quant = self.env['stock.quant'].search(['&',('product_id', '=', productLine.product_id.id),
                                                                ('location_id', '=', location_id)],limit=1)
                if product_quant:
                    productLine.qty_available = product_quant.qty

    @api.one
    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        if self.product_uom_qty <= 0:
            raise UserError('Product quantity can not be negative or zero!!!')

    ####################################################
    # ORM Overrides methods
    ####################################################