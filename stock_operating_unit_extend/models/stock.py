# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class Stock(models.Model):
    _inherit = 'stock.location'

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