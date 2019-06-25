from odoo import api,models,fields
from odoo.tools.misc import formatLang


class ExecutiveSalesReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_executive_sales"

    # DATE(invoice.date_invoice) + interval'6h' BETWEEN '%s' AND '%s'

    sql_str = """"""
    sql_str_local = """SELECT 
                        area.id AS area_id,
                        area.name,
                        res_user.id AS user_id,
                        res_user.name AS Executive,
                        pt.id AS product_id,
                        pt.name AS Product,
                        SUM(ml.quantity / uom.factor * uom2.factor) AS Qty, 
                        uom.name AS Unit,
                        SUM(ml.credit) AS Val
                    FROM 
                        account_move_line ml
                        LEFT JOIN account_invoice invoice ON invoice.id = ml.invoice_id
                        LEFT JOIN product_product product ON product.id = ml.product_id
                        LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
                        LEFT JOIN product_uom uom ON uom.id = ml.product_uom_id
                        LEFT JOIN product_uom uom2 ON uom2.id = pt.uom_id
                        LEFT JOIN res_partner partner ON partner.id = invoice.partner_id
                        LEFT JOIN res_partner_area area ON area.id = partner.area_id
                        LEFT JOIN res_country country ON country.id = partner.country_id
                        LEFT JOIN res_users users ON users.id = invoice.user_id
                        LEFT JOIN res_partner res_user ON res_user.id = users.partner_id
                    WHERE 
                        ml.credit > 0
    """
    sql_str_foreign = """SELECT 
                        country.id AS country_id,
                        country.name,
                        res_user.id AS user_id,
                        res_user.name AS Executive,
                        pt.id AS product_id,
                        pt.name AS Product,
                        SUM(ml.quantity / uom.factor * uom2.factor) AS Qty, 
                        uom.name AS Unit,
                        SUM(ml.credit) AS Val
                    FROM 
                        account_move_line ml
                        LEFT JOIN account_invoice invoice ON invoice.id = ml.invoice_id
                        LEFT JOIN product_product product ON product.id = ml.product_id
                        LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
                        LEFT JOIN product_uom uom ON uom.id = ml.product_uom_id
                        LEFT JOIN product_uom uom2 ON uom2.id = pt.uom_id
                        LEFT JOIN res_partner partner ON partner.id = invoice.partner_id
                        LEFT JOIN res_partner_area area ON area.id = partner.area_id
                        LEFT JOIN res_country country ON country.id = partner.country_id
                        LEFT JOIN res_users users ON users.id = invoice.user_id
                        LEFT JOIN res_partner res_user ON res_user.id = users.partner_id
                    WHERE 
                        ml.credit > 0
    
    """

    @api.multi
    def render_html(self, docids, data=None):
        header = dict()
        header[0] = 'Executive Name'
        header_data = self.env['product.template'].search([('sale_ok', '=', 1)], order='id ASC')
        for val in header_data:
            header[len(header)] = {val.name: {'Qty': 0, 'Value': 0}}

        # Make the sql
        self.make_sql(data)
        record_objs = self.get_data(data, header_data)

        docargs = {
            'data': data,
            'record_objs': record_objs,
            'header': header,
            'header_data': header_data,
        }
        return self.env['report'].render('samuda_sales_report.report_executive_sales', docargs)

    @api.model
    def make_sql(self, data):
        if data['report_type'] == 'local':
            if data['area_id']:
                self.sql_str_local += " AND area.id = '%s'" % (data['area_id'])

            self.sql_str_local += " AND invoice.date BETWEEN '%s' AND '%s'" %(data['date_from'], data['date_to'])
            self.sql_str_local += " GROUP BY res_user.name,res_user.id,pt.id,pt.name,uom.name,area.name,area.id"
            self.sql_str_local += " ORDER BY area.name,res_user.name,pt.name"
            self.sql_str = self.sql_str_local

        elif data['report_type'] == 'foreign':
            if data['country_id']:
                self.sql_str_foreign += " AND country.id = '%s'" % (data['country_id'])

            self.sql_str_local += " AND invoice.date BETWEEN '%s' AND '%s'" % (data['date_from'], data['date_to'])
            self.sql_str_foreign += " GROUP BY res_user.name,res_user.id,pt.id,pt.name,uom.name,country.name,country.id"
            self.sql_str_foreign += " ORDER BY country.name,res_user.name,pt.name"
            self.sql_str = self.sql_str_foreign

    @api.model
    def get_data(self, data, header_data):
        # default value
        record_objs = dict()
        # For area id and country id
        temp_location_id = 0
        temp_executive_id = 0

        self._cr.execute(self.sql_str)
        for val in self._cr.fetchall():
            if temp_location_id != val[0]:
                # set area id
                temp_location_id = val[0]
                # set executive id
                temp_executive_id = val[2]

                # Add new area object
                record_objs[val[0]] = dict()
                record_objs[val[0]]['area_name'] = val[1] if data['area_id'] or data['report_type'] == 'local' else None
                record_objs[val[0]]['country_name'] = val[1] if data['country_id'] or data['report_type'] == 'foreign' \
                    else None
                # Add new executive object
                record_objs[val[0]]['executive_objs'] = dict()
                record_objs[val[0]]['executive_objs'][val[2]] = dict()
                record_objs[val[0]]['executive_objs'][val[2]]['executive_name'] = val[3]
                # Set default product object
                record_objs[val[0]]['executive_objs'][val[2]]['product_objs'] = {v.id: {
                    'qty': 0,
                    'value': 0
                } for v in header_data}

                # Add product qty and value for executive object
                record_objs[val[0]]['executive_objs'][val[2]]['product_objs'][val[4]]['qty'] = val[6]
                record_objs[val[0]]['executive_objs'][val[2]]['product_objs'][val[4]]['value'] = val[8]

            else:
                if temp_executive_id != val[2]:
                    # set executive id
                    temp_executive_id = val[2]
                    # Add new executive object
                    record_objs[val[0]]['executive_objs'][val[2]] = dict()
                    record_objs[val[0]]['executive_objs'][val[2]]['executive_name'] = val[3]
                    # Set default product object
                    record_objs[val[0]]['executive_objs'][val[2]]['product_objs'] = {v.id: {
                        'qty': 0,
                        'value': 0
                    } for v in header_data}

                    # Add product qty and value for executive object
                    record_objs[val[0]]['executive_objs'][val[2]]['product_objs'][val[4]]['qty'] = val[6]
                    record_objs[val[0]]['executive_objs'][val[2]]['product_objs'][val[4]]['value'] = val[8]

                else:
                    # Add product qty and value for existing executive object
                    record_objs[val[0]]['executive_objs'][val[2]]['product_objs'][val[4]]['qty'] = val[6]
                    record_objs[val[0]]['executive_objs'][val[2]]['product_objs'][val[4]]['value'] = val[8]

        return record_objs
