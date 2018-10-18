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
        return self.env['stock.location'].search([('operating_unit_id', '=', self.env.user.default_operating_unit_id.id),('name','=','Stock')], limit=1).id

    name = fields.Char('Reference',  default=lambda self: _('New'),copy=False,
                       readonly=True, required=True, track_visibility='onchange',
                       states={'draft': [('readonly', False)]})
    reason = fields.Text('Reason',readonly=True, required=True, track_visibility='onchange',
                         states={'draft': [('readonly', False)]})
    request_by = fields.Many2one('res.users', string='Request By', required=True, readonly=True, track_visibility='onchange',
                                 default=lambda self: self.env.user)
    requested_date = fields.Datetime('Request Date', required=True, default=fields.Datetime.now, track_visibility='onchange',)
    approved_date = fields.Datetime('Approved Date', readonly=True, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True, track_visibility='onchange',
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
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
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
    def scrap_confirm(self):
        for scrap in self:
            if not scrap.product_lines:
                raise UserError(_('You cannot confirm which has no line.'))

            res = {
                'state': 'waiting_approval'
            }
            requested_date = self.requested_date
            new_seq = self.env['ir.sequence'].next_by_code_new('stock.scraping',requested_date)
            if new_seq:
                res['name'] = new_seq

            scrap.write(res)

    @api.multi
    def scrap_approve(self):
        picking_id = False
        if self.product_lines:
            picking_id = self._create_pickings_and_procurements()
            picking_objs = self.env['stock.picking'].search([('id', '=', picking_id)])
            picking_objs.action_confirm()
            picking_objs.force_assign()

        res = {
            'state': 'approved',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'picking_id': picking_id
        }

        self.write(res)

    @api.model
    def _create_pickings_and_procurements(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in self.product_lines:
            date_planned = datetime.datetime.strptime(self.requested_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('default_location_dest_id', '=', self.scrap_location_id.id),('operating_unit_id', '=', self.operating_unit_id.id)])
                    if not picking_type:
                        raise UserError(_('Please create picking type for scraping.'))

                    pick_name = self.env['stock.picking.type'].browse(picking_type.id).sequence_id.next_by_id()
                    res = {
                        'picking_type_id': picking_type.id,
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.company_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'state': 'done',
                        'invoice_state': 'none',
                        'origin': self.name,
                        'name': pick_name,
                        'date': self.requested_date,
                        'partner_id': self.request_by.partner_id.id or False,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.scrap_location_id.id,
                    }
                    self.picking_type_id = picking_type.id
                    picking = picking_obj.create(res)
                    if picking:
                        picking_id = picking.id

                location_id = self.location_id.id

                moves = {
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
                    'picking_type_id': picking_type.id,

                }
                move_obj.create(moves)

        return picking_id

    @api.multi
    def scrap_reject(self):
        res = {
            'state': 'reject',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)

    @api.multi
    def action_draft(self):
        res = {
            'state': 'draft',
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

    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        if users_obj.has_group('stock.group_stock_manager'):
            domain = [
                ('state', 'in', ['waiting_approval'])]
            return domain
        else:
            return False

class GBSStockScrapLines(models.Model):
    _name = 'gbs.stock.scrap.line'
    _description = 'GBS Stock Scrap Line'
    _order = 'id desc'

    stock_scrap_id = fields.Many2one('gbs.stock.scrap', string='Stock Scrap', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one(related='product_id.uom_id', string='Unit of Measure', required=True)
    qty_available = fields.Float('In Stock',compute = '_compute_quantity',store = True)
    name = fields.Char(related='product_id.name',string='Specification')
    sequence = fields.Integer('Sequence')

    ####################################################
    # Business methods
    ####################################################
    @api.depends('product_id')
    @api.one
    def _compute_quantity(self):
        if self.product_id:
            location_id = self.stock_scrap_id.location_id.id
            product_quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                            ('location_id', '=', location_id)])
            quantity = sum([val.qty for val in product_quant])

            if quantity <= 0:
                raise UserError(_('Product "{0}" has not sufficient balance for this location'.format(self.product_id.display_name)))
            self.qty_available = quantity

    @api.multi
    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        for product in self:
            if product.product_uom_qty <= 0:
                raise UserError('Product quantity can not be negative or zero!!!')

            if product.product_uom_qty > product.qty_available:
                raise UserError('Product quantity can not be greater then available stock!!!')

    ####################################################
    # ORM Overrides methods
    ####################################################