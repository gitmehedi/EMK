from odoo import api, models

class StockPurchaseReport(models.AbstractModel):
    _name = 'report.stock_purchase_custom_report.purchase_report_template'

    @api.multi
    def render_html(self, docids, data=None):

        get_data = self.get_report_data(data)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['category'],
            'total': get_data['total'],

        }
        return self.env['report'].render('stock_custom_summary_report.stock_report_template', docargs)
