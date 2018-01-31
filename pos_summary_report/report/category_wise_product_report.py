from datetime import datetime

from openerp import api, models


class CategoryWiseProductReport(models.AbstractModel):
    _name = 'report.pos_summary_report.report_category_wise_product_report_qweb'

    @api.multi
    def render_html(self, data=None):
        lines, grand = [], {}
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'pos_summary_report.report_category_wise_product_report_qweb')

        domain = []
        if data['shop_id']:
            domain.append(('shop_id', '=', data['shop_id']))

        location = self.env['stock.location'].search([('operating_unit_id', '=', data['shop_id'])])
        quant = self.env['stock.quant'].search([('location_id', '=', location.id)])
        lines = {rec.name: [] for rec in self.env['product.category'].search([])}

        for record in quant:
            rec = {}
            rec['product_name'] = record.product_id.display_name
            rec['barcode'] = record.product_id.default_code
            rec['uom'] = record.product_id.uom_id.name
            rec['sale_price'] = record.product_id.list_price
            rec['cost_price'] = record.product_id.standard_price
            rec['total_value'] = record.inventory_value
            rec['quantity'] = record.qty
            lines[record.product_id.product_tmpl_id.categ_id.name].append(rec)

        # total = sum([val['quantity'] for vals in lines for val in vals])

        op_unit = self.env['operating.unit'].search([('id', '=', data['shop_id'])])
        data['shop_name'] = op_unit.name

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'record': data,
            'total': 0,
            'lines': lines

        }
        return report_obj.render('pos_summary_report.report_category_wise_product_report_qweb', docargs)

    def format_date(self, date):
        return datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d-%m-%Y %H:%M:%S')

    def decimal(self, val):
        return "{:,}".format(round(val, 0))
