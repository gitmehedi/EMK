# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class Stock(models.Model):
    _inherit = 'stock.location'

    usage = fields.Selection([
        ('supplier', 'Vendor Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('procurement', 'Procurement'),
        ('production', 'Production'),
        ('departmental', 'Departmental'),
        ('transit', 'Transit Location')], string='Location Type',
        default='internal', index=True, required=True,
        help="* Vendor Location: Virtual location representing the source location for products coming from your vendors"
             "\n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products"
             "\n* Internal Location: Physical locations inside your own warehouses,"
             "\n* Customer Location: Virtual location representing the destination location for products sent to your customers"
             "\n* Inventory Loss: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)"
             "\n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (vendor or production) is not known yet. This location should be empty when the procurement scheduler has finished running."
             "\n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products"
             "\n* Departmental: Virtual Department location for Department operations: this location use to consume issued product"
             "\n* Transit Location: Counterpart location that should be used in inter-companies or inter-warehouses operations")

    @api.multi
    @api.constrains('operating_unit_id')
    def _check_required_operating_unit(self):
        pass

    @api.multi
    def write(self, values):
        if values.get('operating_unit_id'):
            location_ids = self.search([('location_id', '=', self.id)])
            for location in location_ids:
                if location.operating_unit_id:
                    if values['operating_unit_id'] != location.operating_unit_id.id:
                        raise ValidationError(_('The chosen operating unit is not in the child locations of its'))
        res = super(Stock, self).write(values)
        return res

    @api.multi
    def name_get(self):
        ret_list = []
        for location in self:
            orig_location = location
            name = location.sudo().name
            while location.sudo().location_id and location.sudo().usage != 'view':
                location = location.sudo().location_id
                name = location.sudo().name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.constrains('operating_unit_id', 'location_id', 'picking_id',
                    'operating_unit_dest_id', 'location_dest_id')
    def _check_stock_move_operating_unit(self):
        pass

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', related='warehouse_id.operating_unit_id')