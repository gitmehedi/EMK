from odoo import api, models, fields
from odoo.tools.misc import formatLang


class YearlySalesComparisonReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_yearly_sales_comparison"

    sql_str = """SELECT
                    to_char(invoice.date_invoice, 'YYYY') AS sales_year, 
                    pt.id AS product_id,
                    pt.name AS product_name,
                    to_char(invoice.date_invoice, 'MM') AS sales_month,
                    SUM(ml.quantity / uom.factor * uom2.factor) AS qty,
                    SUM(ml.credit) AS value
                FROM 
                    account_move_line ml
                    LEFT JOIN account_invoice invoice ON invoice.id = ml.invoice_id AND invoice.type = 'out_invoice'
                    LEFT JOIN product_product product ON product.id = ml.product_id
                    LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
                    LEFT JOIN product_uom uom ON uom.id = ml.product_uom_id
                    LEFT JOIN product_uom uom2 ON uom2.id = pt.uom_id
                WHERE 
                    ml.credit > 0 AND pt.active = true AND to_char(invoice.date_invoice, 'YYYY') IN (%s, %s)
                GROUP BY pt.id, pt.name, sales_year, sales_month
                ORDER BY sales_year, pt.name, sales_month
    """

    @api.multi
    def render_html(self, docids, data=None):
        header_data = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep',
                       10: 'Oct', 11: 'Nov', 12: 'Dec'}

        report_data = self.get_data(data, header_data)

        docargs = {
            'data': data,
            'header_data': header_data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_yearly_sales_comparison', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.model
    def get_data(self, data, header_data):
        report_data = dict()

        temp_year = None
        temp_product_id = None

        self._cr.execute(self.sql_str, (data['year_first'], data['year_last']))
        for val in self._cr.fetchall():
            if temp_year != val[0] and val[0] not in report_data:
                temp_year = val[0]
                temp_product_id = val[1]

                report_data[val[0]] = dict()
                report_data[val[0]]['year'] = val[0]
                report_data[val[0]]['products'] = dict()
                report_data[val[0]]['products'][val[1]] = dict()
                report_data[val[0]]['products'][val[1]]['product_name'] = val[2]
                report_data[val[0]]['products'][val[1]]['months'] = {h: {'qty': 0, 'val': 0} for h in header_data}
                report_data[val[0]]['products'][val[1]]['months'][int(val[3])]['qty'] = float(val[4])
                report_data[val[0]]['products'][val[1]]['months'][int(val[3])]['val'] = float(val[5])
            else:
                if temp_product_id != val[1] and val[1] not in report_data[val[0]]['products']:
                    report_data[val[0]]['products'][val[1]] = dict()
                    report_data[val[0]]['products'][val[1]]['product_name'] = val[2]
                    report_data[val[0]]['products'][val[1]]['months'] = {h: {'qty': 0, 'val': 0} for h in header_data}
                    report_data[val[0]]['products'][val[1]]['months'][int(val[3])]['qty'] = float(val[4])
                    report_data[val[0]]['products'][val[1]]['months'][int(val[3])]['val'] = float(val[5])
                else:
                    report_data[val[0]]['products'][val[1]]['months'][int(val[3])]['qty'] = float(val[4])
                    report_data[val[0]]['products'][val[1]]['months'][int(val[3])]['val'] = float(val[5])

        return report_data
