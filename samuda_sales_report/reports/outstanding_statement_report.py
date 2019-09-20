from odoo import api, models, fields
from odoo.tools.misc import formatLang


class OutstandingStatementReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_outstanding_statement"

    sql_str = """SELECT 
                    first_set.user_id,
                    first_set.executive_name,
                    first_set.total_sale_value,
                    second_set.credit_value,
                    (second_set.credit_value/first_set.total_sale_value * 100) AS outstanding_percentage
                FROM
                    (SELECT 
                        users.id AS user_id,
                        executive.name AS executive_name,
                        SUM(ml.credit) AS total_sale_value
                    FROM 
                        account_move_line ml
                        JOIN account_invoice invoice ON invoice.id = ml.invoice_id AND invoice.type = 'out_invoice'
                        JOIN res_users users ON users.id = invoice.user_id
                        JOIN res_partner executive ON executive.id = users.partner_id
                    WHERE 
                        ml.credit > 0 AND DATE(invoice.date_invoice) BETWEEN %s AND %s
                    GROUP BY users.id, executive.name
                    ORDER BY executive.name) AS first_set
                LEFT JOIN 
                    (SELECT 
                        users.id AS user_id,
                        executive.name AS executive_name,
                        SUM(ml.credit) AS credit_value
                    FROM 
                        account_move_line ml
                        JOIN account_invoice invoice ON invoice.id = ml.invoice_id AND invoice.type = 'out_invoice'
                        JOIN sale_order_type so_type ON so_type.id = invoice.sale_type_id 
                                                    AND so_type.sale_order_type NOT IN ('cash','tt_sales')
                        JOIN res_users users ON users.id = invoice.user_id
                        JOIN res_partner executive ON executive.id = users.partner_id
                    WHERE 
                        ml.credit > 0 AND DATE(invoice.date_invoice) BETWEEN %s AND %s
                    GROUP BY users.id, executive.name
                    ORDER BY executive.name) AS second_set 
                                                           ON first_set.user_id = second_set.user_id
    """

    @api.multi
    def render_html(self, docids, data=None):
        # data type list
        report_data = self.get_data(data)

        docargs = {
            'data': data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_outstanding_statement', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.model
    def get_data(self, data):
        # Default report data
        report_data = list()

        if data['executive_id']:
            self.sql_str += " WHERE first_set.user_id = %s" % (data['executive_id'])
        self.sql_str += " ORDER BY first_set.executive_name"

        # execute query
        self._cr.execute(self.sql_str, (data['date_from'], data['date_to'], data['date_from'], data['date_to']))

        # fetch data, make object
        for val in self._cr.fetchall():
            temp_dict = dict()
            temp_dict['sales_person'] = val[1]
            temp_dict['total_sale_value'] = val[2]
            temp_dict['credit_value'] = val[3] if val[3] else 0
            temp_dict['percentage'] = val[4] if val[3] else 0

            report_data.append(temp_dict)

        return report_data
