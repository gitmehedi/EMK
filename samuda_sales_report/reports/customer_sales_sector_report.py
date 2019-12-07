from odoo import api, models, fields
from odoo.tools.misc import formatLang


class CustomerSalesSectorReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_customer_sales_sector"

    sql_str = """SELECT 
                    sector.id AS sector_id,
                    sector.name AS sector_name,
                    customer.id AS customer_id,
                    customer.name AS customer_name,
                    pt.id AS product_id,
                    pt.name AS product_name,
                    SUM(ml.quantity / uom.factor * uom2.factor) AS qty, 
                    SUM(ml.credit) AS val
                FROM 
                    account_move_line ml
                    LEFT JOIN account_invoice invoice ON invoice.id = ml.invoice_id
                    LEFT JOIN product_product product ON product.id = ml.product_id
                    LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
                    LEFT JOIN product_uom uom ON uom.id = ml.product_uom_id
                    LEFT JOIN product_uom uom2 ON uom2.id = pt.uom_id
                    LEFT JOIN res_partner customer ON customer.id = invoice.partner_id
                    RIGHT JOIN res_partner_category sector ON sector.id = customer.sector_id
                WHERE 
                    ml.credit > 0 AND invoice.type = 'out_invoice' AND pt.active = true
    """

    @api.multi
    def render_html(self, docids, data=None):
        header_data = self.env['product.template'].search([('sale_ok', '=', 1), ('active', '=', 1)], order='id ASC')
        report_data = self.get_data(data, header_data)
        docargs = {
            'data': data,
            'header_data': header_data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_customer_sales_sector', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.model
    def get_sql(self, data):
        # Make SQL
        if data['sector_id']:
            self.sql_str += " AND sector.id = '%s'" % (data['sector_id'])

        self.sql_str += " AND DATE(invoice.date) BETWEEN '%s' AND '%s'" % (data['date_from'], data['date_to'])
        self.sql_str += " GROUP BY customer.id, customer.name, pt.id, pt.name, sector.id, sector.name"
        self.sql_str += " ORDER BY sector.id, customer.id, pt.id"

        return self.sql_str

    @api.model
    def get_data(self, data, header_data):
        # Default report data
        report_data = dict()

        # Temporary variable
        temp_sector_id = 0
        temp_customer_id = 0

        # Execute the SQL
        self._cr.execute(self.get_sql(data))
        # Make dictionary objects for report_data variable
        for val in self._cr.fetchall():
            if temp_sector_id != val[0]:
                temp_sector_id = val[0]
                temp_customer_id = val[2]

                # Add new area object
                report_data[val[0]] = dict()
                report_data[val[0]]['sector_name'] = val[1]
                # Add new customer object
                report_data[val[0]]['customers'] = dict()
                report_data[val[0]]['customers'][val[2]] = dict()
                report_data[val[0]]['customers'][val[2]]['customer_name'] = val[3]
                # Set default product object
                report_data[val[0]]['customers'][val[2]]['products'] = {v.id: {
                    'qty': 0,
                    'val': 0
                } for v in header_data}

                # Add product qty and value for customer object
                report_data[val[0]]['customers'][val[2]]['products'][val[4]]['qty'] = val[6]
                report_data[val[0]]['customers'][val[2]]['products'][val[4]]['val'] = val[7]

            else:
                if temp_customer_id != val[2]:
                    temp_customer_id = val[2]

                    # Add new customer object
                    report_data[val[0]]['customers'][val[2]] = dict()
                    report_data[val[0]]['customers'][val[2]]['customer_name'] = val[3]
                    # Set default product object
                    report_data[val[0]]['customers'][val[2]]['products'] = {v.id: {
                        'qty': 0,
                        'val': 0
                    } for v in header_data}

                    # Add product qty and value for customer object
                    report_data[val[0]]['customers'][val[2]]['products'][val[4]]['qty'] = val[6]
                    report_data[val[0]]['customers'][val[2]]['products'][val[4]]['val'] = val[7]

                else:
                    # Add product qty and value for existing customer object
                    report_data[val[0]]['customers'][val[2]]['products'][val[4]]['qty'] = val[6]
                    report_data[val[0]]['customers'][val[2]]['products'][val[4]]['val'] = val[7]

        return report_data
