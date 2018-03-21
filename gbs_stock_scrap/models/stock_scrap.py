# -*- coding: utf-8 -*-
import time
import datetime

from openerp import models, fields, api, _
from openerp.addons import decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning


class GBSStockScrap(models.Model):
    _name = 'gbs.stock.scrap'
    _description = 'GBS Stock Scrap'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    def _default_scrap_location(self):
        return self.env['stock.location'].search([('scrap_location', '=', True)], limit=1)

    def _default_location(self):
        return self.env['stock.location'].search(
            [('operating_unit_id', '=', self.env.user.default_operating_unit_id.id)], limit=1)

    name = fields.Char('Reference', default=lambda self: _('New'), copy=False,
                       readonly=True, required=True,
                       states={'draft': [('readonly', False)]})
    reason = fields.Text('Reason', readonly=True, required=True,
                         states={'draft': [('readonly', False)]})
    request_by = fields.Many2one('res.users', string='Request By', required=True, readonly=True,
                                 default=lambda self: self.env.user)
    requested_date = fields.Datetime('Request Date', required=True, default=fields.Datetime.now)
    approved_date = fields.Datetime('Approved Date', readonly=True)
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True,
                                  help="who have approve or reject.")
    location_id = fields.Many2one('stock.location', 'Location', default=_default_location,
                                  domain="[('usage', '=', 'internal'),('operating_unit_id', '=',operating_unit_id)]",
                                  required=True, states={'draft': [('readonly', False)]})
    scrap_location_id = fields.Many2one('stock.location', 'Scrap Location', default=_default_scrap_location,
                                        domain="[('scrap_location', '=', True)]", readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    picking_id = fields.Many2one('stock.picking', 'Picking', states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')

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
                raise Warning(_('You cannot confirm which has no line.'))

            res = {
                'state': 'waiting_approval'
            }
            new_seq = self.env['ir.sequence'].next_by_code('stock.scraping')
            if new_seq:
                res['name'] = new_seq

            scrap.write(res)

    @api.multi
    def scrap_approve(self):
        picking_id = False
        if self.product_lines:
            picking_id = self._create_pickings_and_procurements()

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
                        [('default_location_src_id', '=', self.location_id.id),
                         ('default_location_dest_id', '=', self.scrap_location_id.id), ('code', '=', 'internal')])
                    if not picking_type:
                        raise Warning(_('Please create picking type for product scraping.'))

                    res = {
                        'picking_type_id': picking_type.id,
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.env.user['company_id'].id,
                        'dest_operating_unit_id': self.operating_unit_id.id,
                        'stock_transfer_id': self.id,
                        'state': 'done',
                        'invoice_state': 'none',
                        'origin': self.name,
                        'date': self.requested_date,
                    }
                    if self.company_id:
                        vals = dict(res, company_id=self.company_id.id)

                    picking = picking_obj.create(vals)
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
                move = move_obj.create(moves)
                move.action_done()
                self.write({'move_id': move.id})

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
    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', '=', self.picking_id.id)]
        return action

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise Warning(_('You cannot delete this !!'))
        return super(GBSStockScrap, self).unlink()


class GBSStockScrapLines(models.Model):
    _name = 'gbs.stock.scrap.line'
    _description = 'GBS Stock Scrap Line'
    _order = 'id desc'

    name = fields.Text('Specification', store=True)
    sequence = fields.Integer('Sequence')

    stock_scrap_id = fields.Many2one('gbs.stock.scrap', string='Stock Scrap', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one(related='product_id.uom_id', string='Unit of Measure', required=True)
    qty_available = fields.Float('In Stock')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            location_id = self.env['pos.config'].search(
                [('operating_unit_id', '=', self.stock_scrap_id.operating_unit_id.id)], limit=1)
            quant = self.env['stock.quant'].search(
                [('product_id', '=', self.product_id.id), ('location_id', '=', location_id.stock_location_id.id)])

            self.qty_available = sum([val.qty for val in quant])

    @api.one
    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        if self.product_uom_qty <= 0:
            raise Warning('Product quantity can not be negative or zero!!!')
