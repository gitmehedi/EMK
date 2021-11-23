import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class StockIndentScrap(models.Model):
    _name = 'stock.indent.scrap'
    _description = "Scrap"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def _get_default_warehouse(self):
        warehouse_obj = self.env['stock.warehouse']
        company_id = self.env.user.company_id.id
        warehouse_ids = warehouse_obj.sudo().search(
            [('company_id', '=', company_id), ('operating_unit_id', 'in', self.env.user.operating_unit_ids.ids)])
        warehouse_id = warehouse_ids and warehouse_ids[0] or False
        return warehouse_id

    @api.multi
    def _default_department(self):
        emp_ins = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if not emp_ins.department_id:
            raise ValidationError(
                _("Please configure employee for user [{0}] from employee directory.".format(
                    self.env.user.display_name)))
        return emp_ins.department_id

    def _get_default_scrap_location_id(self):
        return self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in',
                                                                                  [self.env.user.company_id.id, False])], limit=1).id

    @api.multi
    @api.depends('warehouse_id', 'stock_location_id')
    def _compute_default_picking_type(self):
        for indent in self:
            picking_type_obj = indent.env['stock.picking.type']
            picking_type_ids = picking_type_obj.search(
                [('default_location_src_id', '=', indent.warehouse_id.sudo().lot_stock_id.id),
                 ('default_location_dest_id', '=', indent.stock_location_id.id)])
            picking_type_id = picking_type_ids and picking_type_ids[0] or False
            indent.picking_type_id = picking_type_id
            if picking_type_id:
                indent.picking_type_id = picking_type_id

    name = fields.Char('Scrap #', size=30, readonly=True, track_visibility="onchange")
    """ Approval Process User """
    requestor_id = fields.Many2one('res.users', string='Requestor', required=True, readonly=True,
                                   default=lambda self: self.env.user,
                                   states={'draft': [('readonly', False)]}, track_visibility="onchange")
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True,
                                  help="who have approve or reject scrap.", track_visibility="onchange")
    approve_date = fields.Datetime('Approve Date', readonly=True, track_visibility="onchange")
    closer_id = fields.Many2one('res.users', string='Authority', readonly=True, help="who have close indent.")
    scrap_date = fields.Datetime('Scrap Date', required=True, readonly=True,
                                 default=fields.Datetime.now, track_visibility="onchange")

    """ Relational Fields """
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True, required=True,
                                   default=lambda self: self._get_default_warehouse(),
                                   help="Default Warehouse.Source location.",
                                   states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                   track_visibility="onchange")
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, default=_default_department,
                                    track_visibility="onchange")
    stock_location_id = fields.Many2one('stock.location', string='Stock Location', readonly=True, required=True,
                                        states={'draft': [('readonly', False)]},
                                        help="Default User Location.Destination location.",
                                        default=lambda self: self.env.user.default_location_id,
                                        track_visibility="onchange")
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True)]", states={'done': [('readonly', True)]})
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    picking_id = fields.Many2one('stock.picking', 'Picking', states={'done': [('readonly', True)]})
    # scrap_qty = fields.Float('Quantity', default=1.0, required=True, states={'done': [('readonly', True)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True,
                                 track_visibility="onchange")
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type',
                                      compute='_compute_default_picking_type',
                                      readonly=True, store=True, track_visibility="onchange")
    product_lines = fields.One2many('scrap.product.lines', 'scrap_id', 'Products', readonly=True, required=True,
                                    states={'draft': [('readonly', False)],
                                            'waiting_approval': [('readonly', False)],
                                            'done': [('readonly', True)]}, track_visibility="onchange")

    material_scrap_remarks = fields.Text('Scrap Remarks', readonly=True, states={'draft': [('readonly', False)]},
                                         track_visibility="onchange")

    """ States Fields """
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting_approval', 'Waiting for Approval'),
        ('done', 'Done'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    def scrap_confirm(self):
        for scrap in self:
            if not scrap.product_lines:
                raise UserError(_('Unable to confirm scrap without product. Please add product(s).'))
        for scrap_product in self.product_lines:
            if scrap_product.qty_available <=0:
                raise UserError('Stock not available!!!')
            if scrap_product.qty_available < scrap_product.scrap_qty:
                raise UserError('The requested quantity is not available!!! ')
            if scrap_product.scrap_qty <= 0:
                raise UserError('The requested quantity is not valid!!! ')
            res = {
                'state': 'waiting_approval'
            }
            new_seq = self.env['ir.sequence'].next_by_code('stock.indent.scrap') or _('New')
            if new_seq:
                res['name'] = new_seq

            scrap.write(res)
            scrap.product_lines.write({'state':'waiting_approval'})

    def reject_scrap(self):
        for scrap in self:
            if scrap.state == 'done':
                raise UserError(_('Unable to reject scrap after done state'))

            scrap.write({'state':'reject'})
            scrap.product_lines.write({'state':'reject'})

    def approve_scrap(self):
        if self.state != 'waiting_approval':
            raise ValidationError(_('Please scrap product in validate state.'))
        for scrap in self:
            for line in self.product_lines:
                moves_obj = self.env['stock.move']
                moves_vals = {
                    'name': self.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'product_uom_qty': line.scrap_qty,
                    'location_id': self.stock_location_id.id,
                    'scrapped': True,
                    'location_dest_id': self.scrap_location_id.id,
                    # 'restrict_lot_id': self.lot_id.id,
                    # 'restrict_partner_id': self.owner_id.id,
                    'picking_id': self.picking_id.id,
                    'state':'done'
                }
                moves = moves_obj.create(moves_vals)
                moves.action_done()
                # quant_obj = self.env['stock.quant']
                # quant_vals = {
                #     'location_id': self.scrap_location_id.id,
                #     'qty': line.scrap_qty,
                #     'company_id': self.company_id.id,
                #     'product_id': line.product_id.id,
                #     'in_date': self.scrap_date
                # }
                # quant = quant_obj.create(quant_vals)

            res = {
                'state': 'done',
                'approver_id': self.env.user.id,
                'approve_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'move_id': moves.id
            }
            scrap.write(res)
            scrap.product_lines.write({'state': 'done'})


class ScrapProductLines(models.Model):
    _name = 'scrap.product.lines'
    _description = "Scrap Product Line"

    scrap_id = fields.Many2one('stock.indent.scrap', string='Scrap', required=True, ondelete='cascade',track_visibility='onchange')
    product_id = fields.Many2one('product.product',string='Product',required=True, ondelete='cascade',track_visibility='onchange')
    product_uom = fields.Many2one(related='product_id.uom_id', comodel='product.uom', string='Unit of Measure',
                                  required=True, store=True, track_visibility='onchange')
    qty_available = fields.Float(string='In Stock', compute='_compute_product_qty', track_visibility='onchange')
    scrap_qty = fields.Float(string='Scrap Quantity',  track_visibility='onchange')
    name = fields.Char(related='product_id.name', string='Specification', store=True, track_visibility='onchange')
    remarks = fields.Char(related='product_id.name', string='Narration', store=True, track_visibility='onchange')
    sequence = fields.Integer('Sequence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting_approval', 'Waiting for Approval'),
        ('done', 'Done'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.depends('product_id')
    @api.multi
    def _compute_product_qty(self):
        for product in self:
            location_id = product.scrap_id.warehouse_id.sudo().lot_stock_id.id
            product_quant = self.env['stock.quant'].search(
                [('product_id', '=', product.product_id.id), ('location_id', '=', location_id)])
            quantity = sum([val.qty for val in product_quant])
            product.qty_available = quantity
