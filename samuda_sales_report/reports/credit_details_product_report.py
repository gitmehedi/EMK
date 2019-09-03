from odoo import api, models, fields
from odoo.tools.misc import formatLang


class CreditDetailsProductReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_credit_details_product"

    sql_str = """SELECT 
                    pt.id AS product_id,
                    pt.name AS product_name,
                    customer.name AS customer_name,
                    DATE(invoice.create_date) AS delivery_date,
                    SUM(ml.quantity / uom.factor * uom2.factor) AS qty,
                    SUM(ml.credit) AS value,
                    apt_line.days AS credit_tenure,
                    invoice.date_due AS maturity_date
                FROM 
                    account_move_line ml
                    LEFT JOIN account_invoice invoice ON invoice.id = ml.invoice_id 
                                                    AND invoice.type = 'out_invoice' AND invoice.state != 'paid'
                    LEFT JOIN product_product product ON product.id = ml.product_id
                    LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
                    LEFT JOIN product_uom uom ON uom.id = ml.product_uom_id
                    LEFT JOIN product_uom uom2 ON uom2.id = pt.uom_id
                    LEFT JOIN res_partner customer ON customer.id = invoice.partner_id
                    RIGHT JOIN sale_order_type sot ON sot.id = invoice.sale_type_id 
                                                 AND sot.sale_order_type IN ('credit_sales','lc_sales','contract_sales')
                    LEFT JOIN account_payment_term apt ON apt.id = invoice.payment_term_id
                    LEFT JOIN account_payment_term_line apt_line ON apt_line.payment_id = apt.id 
                                                                AND apt_line.value = 'balance'
    """

    @api.multi
    def render_html(self, docids, data=None):
        # data type dictionary
        report_data = self.get_data(data)
        docargs = {
            'data': data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_credit_details_product', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.model
    def get_data(self, data):
        report_data = dict()

        self.sql_str += " WHERE ml.credit > 0"
        if data['product_id']:
            self.sql_str += " AND pt.id = %s" % (data['product_id'])
        self.sql_str += " GROUP BY pt.id, pt.name, customer.name, DATE(invoice.create_date), " \
                        "apt_line.days, invoice.date_due ORDER BY pt.name, customer.name, DATE(invoice.create_date)"
        self._cr.execute(self.sql_str)

        temp_product_id = None

        for val in self._cr.fetchall():
            if temp_product_id != val[0] and val[0] not in report_data:
                temp_product_id = val[0]
                report_data[val[0]] = dict()
                report_data[val[0]]['product_name'] = val[1]
                report_data[val[0]]['customers'] = list()
                report_data[val[0]]['customers'].append({'customer_name': val[2], 'delivery_date': val[3],
                                                         'qty': float(val[4]), 'val': float(val[5]),
                                                         'credit_tenure': val[6], 'maturity_date': val[7]})

            else:
                report_data[val[0]]['customers'].append({'customer_name': val[2], 'delivery_date': val[3],
                                                         'qty': float(val[4]), 'val': float(val[5]),
                                                         'credit_tenure': val[6], 'maturity_date': val[7]})

        return report_data
