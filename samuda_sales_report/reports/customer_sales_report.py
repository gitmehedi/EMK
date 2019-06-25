from odoo import api,models,fields
from odoo.tools.misc import formatLang


class CustomerSalesReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_customer_sales"

    sql_str = """ """

    @api.multi
    def render_html(self, docids, data=None):
        header = dict()
        header[0] = 'Party Name'
        header_data = self.env['product.template'].search([('sale_ok', '=', 1)], order='id ASC')
        for val in header_data:
            header[len(header)] = {val.name: {'Qty': 0, 'Value': 0}}

        # area or country wise sales objects
        record_objs = {0: {
            'area_name': data['area_name'] if data['area_id'] else None,
            'country_name': data['country_name'] if data['country_id'] else None,
            'customer_objs': {
                0: {
                    'customer_name': 'Mohammad Amir',
                    'product_objs': {v.id: {
                        'qty': 10,
                        'value': 20
                    } for v in header_data}},
                1: {
                    'customer_name': 'Said Anwar',
                    'product_objs': {v.id: {
                        'qty': 20,
                        'value': 10
                    } for v in header_data}}}},
            1: {
            'area_name': data['area_name'] if data['area_id'] else None,
            'country_name': data['country_name'] if data['country_id'] else None,
            'customer_objs': {
                0: {
                    'customer_name': 'kan',
                    'product_objs': {v.id: {
                        'qty': 0,
                        'value': 0
                    } for v in header_data}},
                1: {
                    'customer_name': 'Jhon',
                    'product_objs': {v.id: {
                        'qty': 0,
                        'value': 0
                    } for v in header_data}}}}
        }

        docargs = {
            'data': data,
            'record_objs': record_objs,
            'header': header,
            'header_data': header_data,
        }
        return self.env['report'].render('samuda_sales_report.report_customer_sales', docargs)
