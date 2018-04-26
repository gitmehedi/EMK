from datetime import datetime

from openerp import api, models


class DailyCreditSettlementReport(models.AbstractModel):
    _name = 'report.product_requisition.report_product_usage_summary_report_view_qweb'

    @api.multi
    def render_html(self, data=None):
        lines, grand = {}, {}
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'product_requisition.report_product_usage_summary_report_view_qweb')

        domain = []
        if data['operating_unit_id']:
            domain.append(('operating_unit_id', '=', data['operating_unit_id']))
        if data['start_date']:
            domain.append(('period_id', '>=', data['start_period_id']))
        if data['end_date']:
            domain.append(('period_id', '<=', data['end_period_id']))

        period = self.env['account.period'].search(
            [('id', '>=', data['start_period_id']), ('id', '<=', data['end_period_id']),
             ('special', '=', False)], order='id asc')

        records = self.env['product.usage.history'].search(domain, order="product_id asc,write_date asc")

        header = {}
        header[0] = 'SI'
        header[1] = 'Product Name'
        for pr in period:
            header[len(header)] = pr.name
        header[len(header)] = 'Total'
        header[len(header)] = 'Average'

        for record in records:
            name = record.product_id.display_name
            if name not in lines:
                lines[name] = {}
                lines[name]['period'] = {val.name: 0.0 for val in period}
                lines[name]['value'] = 0.0
                lines[name]['no_of_value'] = 0.0
                lines[name]['average'] = 0.0
            lines[name]['period'][record.period_id.name] = record.value
            lines[name]['value'] = lines[name]['value'] + record.value
            if record.value:
                lines[name]['no_of_value'] = lines[name]['no_of_value'] + 1
                lines[name]['average'] = round(lines[name]['value'] / lines[name]['no_of_value'], 2)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'record': data,
            'header': header,
            'lines': lines
        }
        return report_obj.render('product_requisition.report_product_usage_summary_report_view_qweb', docargs)

    def format_date(self, date):
        return datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d-%m-%Y %H:%M:%S')

    def decimal(self, val):
        return "{:,}".format(round(val, 0))
