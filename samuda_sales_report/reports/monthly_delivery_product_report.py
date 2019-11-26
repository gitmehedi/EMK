from odoo import api, models, fields
from odoo.tools.misc import formatLang


class MonthlyDeliveryProductReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_monthly_delivery_product"

    sql_str = """SELECT 
                    customer.id AS customer_id,
                    customer.name AS customer_name,
                    CAST(to_char(invoice.date_invoice, 'DD') AS INTEGER) AS invoice_day,
                    SUM(ml.quantity / uom.factor * uom2.factor) AS qty, 
                    SUM(ml.credit) AS val
                FROM 
                    account_move_line ml
                    LEFT JOIN account_invoice invoice ON invoice.id = ml.invoice_id AND invoice.type = 'out_invoice'
                    LEFT JOIN sale_order so ON so.id = invoice.so_id
                    LEFT JOIN product_product product ON product.id = ml.product_id
                    LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
                    LEFT JOIN product_uom uom ON uom.id = ml.product_uom_id
                    LEFT JOIN product_uom uom2 ON uom2.id = pt.uom_id
                    LEFT JOIN res_partner customer ON customer.id = invoice.partner_id
                WHERE 
                    ml.credit > 0  AND pt.active = true AND pt.id = %s AND so.region_type = %s
                    AND CAST(to_char(invoice.date_invoice, 'MM') AS INTEGER) = %s 
                    AND CAST(to_char(invoice.date_invoice, 'YYYY') AS INTEGER) = %s
                GROUP BY
                    customer.id, customer.name, invoice_day
                ORDER BY 
                    customer.name
    """

    @api.multi
    def render_html(self, docids, data=None):
        # list
        header_data = [d for d in range(1, data['month_days'] + 1)]
        # list
        report_data = self.get_data(data, header_data)
        # calculate total qty and val for each customer
        total = dict()
        for key in report_data:
            temp_dict = dict()
            temp_dict['qty'] = sum(report_data[key]['qty'][k] for k in report_data[key]['qty'])
            temp_dict['val'] = sum(report_data[key]['val'][k] for k in report_data[key]['val'])
            total[key] = temp_dict

        docargs = {
            'data': data,
            'header_data': header_data,
            'report_data': report_data,
            'total': total,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_monthly_delivery_product', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.model
    def get_data(self, data, header_data):
        # Default report data
        report_data = dict()
        # execute query
        self._cr.execute(self.sql_str, (data['product_id'], data['type'], data['month'], data['year']))

        # fetch data, make object
        for val in self._cr.fetchall():
            if val[0] not in report_data:
                report_data[val[0]] = dict()
                report_data[val[0]]['customer_name'] = val[1]

                report_data[val[0]]['qty'] = {v: 0 for v in header_data}
                report_data[val[0]]['val'] = {v: 0 for v in header_data}

                report_data[val[0]]['qty'][val[2]] = float(val[3])
                report_data[val[0]]['val'][val[2]] = float(val[4])
            else:
                report_data[val[0]]['qty'][val[2]] = float(val[3])
                report_data[val[0]]['val'][val[2]] = float(val[4])

        return report_data
