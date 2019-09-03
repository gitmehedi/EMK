from odoo import api, models, fields
from odoo.tools.misc import formatLang


class ExecutiveSalesReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_executive_sales"

    sql_str_local = """SELECT 
                            area.id AS area_id,
                            area.name AS area_name,
                            executive.id AS executive_id,
                            executive.name AS executive_name,
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
                            LEFT JOIN res_partner partner ON partner.id = invoice.partner_id
                            RIGHT JOIN res_partner_area area ON area.id = partner.area_id
                            LEFT JOIN res_country country ON country.id = partner.country_id
                            LEFT JOIN res_users users ON users.id = invoice.user_id
                            LEFT JOIN res_partner executive ON executive.id = users.partner_id
                        WHERE 
                            ml.credit > 0 AND invoice.type = 'out_invoice' AND pt.active = true
                            AND partner.supplier_type = 'local'
    """
    sql_str_foreign = """SELECT 
                            country.id AS country_id,
                            country.name AS country_name,
                            executive.id AS executive_id,
                            executive.name AS executive_name,
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
                            LEFT JOIN res_partner partner ON partner.id = invoice.partner_id
                            LEFT JOIN res_partner_area area ON area.id = partner.area_id
                            RIGHT JOIN res_country country ON country.id = partner.country_id
                            LEFT JOIN res_users users ON users.id = invoice.user_id
                            LEFT JOIN res_partner executive ON executive.id = users.partner_id
                        WHERE 
                            ml.credit > 0 AND invoice.type = 'out_invoice' AND pt.active = true
                            AND partner.supplier_type = 'foreign' AND country.code != 'BD'
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

        return self.env['report'].render('samuda_sales_report.report_executive_sales', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.model
    def get_sql(self, data):
        # Make SQL
        if data['report_type'] == 'local':
            if data['area_id']:
                self.sql_str_local += " AND area.id = '%s'" % (data['area_id'])

            self.sql_str_local += " AND DATE(invoice.date) BETWEEN '%s' AND '%s'" % (data['date_from'], data['date_to'])
            self.sql_str_local += " GROUP BY executive.id, executive.name, pt.id, pt.name, area.id, area.name"
            self.sql_str_local += " ORDER BY area.id, executive.id, pt.id"
            sql = self.sql_str_local
        else:
            # For foreign report
            if data['country_id']:
                self.sql_str_foreign += " AND country.id = '%s'" % (data['country_id'])

            self.sql_str_foreign += " AND DATE(invoice.date) BETWEEN '%s' AND '%s'" % (data['date_from'],
                                                                                       data['date_to'])
            self.sql_str_foreign += " GROUP BY executive.id, executive.name, pt.id, pt.name, country.id, country.name"
            self.sql_str_foreign += " ORDER BY country.id, executive.id, pt.id"
            sql = self.sql_str_foreign

        return sql

    @api.model
    def get_data(self, data, header_data):
        # Default report data
        report_data = dict()

        # Temporary variable
        temp_location_id = 0
        temp_executive_id = 0

        # Execute the SQL
        self._cr.execute(self.get_sql(data))
        # Make dictionary objects for report_data variable
        for val in self._cr.fetchall():
            if temp_location_id != val[0]:
                temp_location_id = val[0]
                temp_executive_id = val[2]

                # Add new area object
                report_data[val[0]] = dict()
                report_data[val[0]]['area_name'] = val[1] if data['report_type'] == 'local' else None
                report_data[val[0]]['country_name'] = val[1] if data['report_type'] == 'foreign' else None
                # Add new executive object
                report_data[val[0]]['executives'] = dict()
                report_data[val[0]]['executives'][val[2]] = dict()
                report_data[val[0]]['executives'][val[2]]['executive_name'] = val[3]
                # Set default product object
                report_data[val[0]]['executives'][val[2]]['products'] = {v.id: {
                    'qty': 0,
                    'val': 0
                } for v in header_data}

                # Add product qty and value for executive object
                report_data[val[0]]['executives'][val[2]]['products'][val[4]]['qty'] = val[6]
                report_data[val[0]]['executives'][val[2]]['products'][val[4]]['val'] = val[7]

            else:
                if temp_executive_id != val[2]:
                    temp_executive_id = val[2]

                    # Add new executive object
                    report_data[val[0]]['executives'][val[2]] = dict()
                    report_data[val[0]]['executives'][val[2]]['executive_name'] = val[3]
                    # Set default product object
                    report_data[val[0]]['executives'][val[2]]['products'] = {v.id: {
                        'qty': 0,
                        'val': 0
                    } for v in header_data}

                    # Add product qty and value for executive object
                    report_data[val[0]]['executives'][val[2]]['products'][val[4]]['qty'] = val[6]
                    report_data[val[0]]['executives'][val[2]]['products'][val[4]]['val'] = val[7]

                else:
                    # Add product qty and value for existing executive object
                    report_data[val[0]]['executives'][val[2]]['products'][val[4]]['qty'] = val[6]
                    report_data[val[0]]['executives'][val[2]]['products'][val[4]]['val'] = val[7]

        return report_data
