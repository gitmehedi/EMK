from datetime import datetime

from openerp import api, models


class DailyCreditSettlementReport(models.AbstractModel):
    _name = 'report.pos_summary_report.report_warehouse_to_shop_distribution_report_view_qweb'

    @api.multi
    def render_html(self, data=None):
        lines, grand = [], {}
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'pos_summary_report.report_warehouse_to_shop_distribution_report_view_qweb')

        domain = []
        if data['source_location_id']:
            domain.append(('location_id', '=', data['source_location_id']))
        if data['destination_location_id']:
            domain.append(('location_dest_id', '=', data['destination_location_id']))
        if data['start_date']:
            domain.append(('date', '>=', data['start_date']))
        if data['end_date']:
            domain.append(('date', '<=', data['end_date']))
        if data['product_id']:
            domain.append(('product_id', '=', data['product_id']))



        moves = self.env['stock.move'].search(domain, order="product_id asc,write_date asc")

        for record in moves:
            rec = {}
            rec['product_name'] = record.product_id.display_name
            rec['barcode'] = record.product_id.default_code
            rec['uom'] = record.product_id.uom_id.name
            rec['create_uid'] = record.create_uid.name
            rec['write_uid'] = record.write_uid.name
            rec['write_date'] = record.write_date
            rec['quantity'] = record.product_qty
            lines.append(rec)

        total = sum([val['quantity'] for val in lines])

        op_unit = self.env['operating.unit'].search([('id', '=', data['operating_unit_id'])])
        data['shop_name'] = op_unit.name

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'record': data,
            'total': total,
            'lines': lines

        }
        return report_obj.render('pos_summary_report.report_warehouse_to_shop_distribution_report_view_qweb', docargs)

    def format_date(self, date):
        return datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d-%m-%Y %H:%M:%S')

    def decimal(self, val):
        return "{:,}".format(round(val, 0))
