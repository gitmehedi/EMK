from odoo import api, models, fields
from odoo.tools.misc import formatLang


class SectorSalesProductReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_sector_sales_product"

    sql_str = """SELECT 
                    pt.id AS product_id,
                    pt.name AS product_name,
                    sector.id AS sector_id,
                    sector.name AS sector_name,    
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
                    RIGHT JOIN res_partner_category sector ON sector.id = partner.sector_id
                WHERE 
                    ml.credit > 0 AND invoice.type = 'out_invoice' AND pt.active = true
    """

    @api.multi
    def render_html(self, docids, data=None):
        report_data = self.get_data(data)
        docargs = {
            'data': data,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_sector_sales_product', docargs)

    @api.multi
    def format_lang(self, value):
        if value == 0:
            return value
        return formatLang(self.env, value)

    @api.model
    def get_sql(self, data):
        # Make SQL
        if data['product_id']:
            self.sql_str += " AND pt.id = '%s'" % (data['product_id'])
        self.sql_str += " AND DATE(invoice.date) BETWEEN '%s' AND '%s'" % (data['date_from'], data['date_to'])
        self.sql_str += " GROUP BY sector.id, sector.name, pt.id, pt.name"
        self.sql_str += " ORDER BY pt.id, sector.id"

        return self.sql_str

    @api.model
    def get_data(self, data):
        # Default report data
        report_data = dict()

        # Temporary variable
        temp_product_id = 0

        # Execute the SQL
        self._cr.execute(self.get_sql(data))
        # Make dictionary objects for report_data variable
        for val in self._cr.fetchall():
            if temp_product_id != val[0]:
                temp_product_id = val[0]

                # Add new area object
                report_data[val[0]] = dict()
                report_data[val[0]]['product_name'] = val[1]
                # Add new customer object
                report_data[val[0]]['sectors'] = list()
                report_data[val[0]]['sectors'].append(
                    {'sector_name': val[3], 'qty': val[4], 'val': val[5], 'ratio': 0})
            else:
                report_data[val[0]]['sectors'].append(
                    {'sector_name': val[3], 'qty': val[4], 'val': val[5], 'ratio': 0})

        # set ratio
        for key in report_data:
            total_value = sum(lst['val'] for lst in report_data[key]['sectors'])
            for index, value in enumerate(report_data[key]['sectors']):
                report_data[key]['sectors'][index]['ratio'] = (value['val'] / total_value) * 100

        return report_data
