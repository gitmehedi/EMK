# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models
import time


class StockInventoryWizard(models.TransientModel):
    _name = 'stock.inventory.wizard'

    date_from = fields.Date("Date from", required=True)
    date_to = fields.Date("Date to", required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit Name', required=True)
    category_id = fields.Many2one('product.category', string='Category', required=False)
    product_id = fields.Many2one('product.product', string='Product')
    report_type_ids = fields.Many2many('report.type.selection', string="Report Type")



    @api.multi
    def report_print(self):
        location = self.env['stock.location'].search([('operating_unit_id', '=', self.operating_unit_id.id),('name', '=', 'Stock')])
        report_type = [val.code for val in self.env['report.type.selection'].search([])]
        selected_type = [val.code for val in self.report_type_ids]

        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['operating_unit_id'] = location.id
        data['operating_unit_name'] = self.operating_unit_id.name
        data['category_id'] = self.category_id.id
        data['product_id'] = self.product_id.id
        data['report_type'] = selected_type if len(selected_type) > 0 else report_type

        return self.env['report'].get_action(self, 'stock_custom_summary_report.stock_report_template',
                                             data=data)
