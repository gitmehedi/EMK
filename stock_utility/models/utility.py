# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockUtility(models.TransientModel):
    _name = 'stock.utility'

    def get_location_id(self, operating_unit_id):
        warehouse_id = self.env['stock.warehouse'].search([('operating_unit_id', '=', operating_unit_id)])
        if warehouse_id:
            location_id = warehouse_id.wh_main_stock_loc_id.id
            if not location_id:
                location_id = self.env['stock.location'].search(
                    [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
                    limit=1).id
        else:
            location_id = self.env['stock.location'].search(
                [('operating_unit_id', '=', operating_unit_id), ('name', '=', 'Stock')],
                limit=1).id
        print(location_id)
        return location_id
