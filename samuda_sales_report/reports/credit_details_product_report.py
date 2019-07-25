from odoo import api, models, fields
from odoo.tools.misc import formatLang


class CreditDetailsProductReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_credit_details_product"

    sql_str = """"""

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
        return formatLang(self.env, value)

    @api.model
    def get_data(self, data):
        # Default report data

        report_data = {
            0: {
                'product_name': 'Test',
                'customers': [
                    {'customer_name': 'ABM Dyeing Ltd.', 'delivery_date': '10/07/2019', 'qty': 100,
                     'val': 25000, 'credit_tenure': 20, 'maturity_date': '30/07/2019'},
                    {'customer_name': 'Test Ltd.', 'delivery_date': '10/07/2019', 'qty': 100,
                     'val': 25000, 'credit_tenure': 20, 'maturity_date': '30/07/2019'}
                ]
            },
            1: {
                'product_name': 'Test 2',
                'customers': [
                    {'customer_name': 'ABM Dyeing Ltd.', 'delivery_date': '10/07/2019', 'qty': 100,
                     'val': 25000, 'credit_tenure': 20, 'maturity_date': '30/07/2019'},
                    {'customer_name': 'Test Ltd.', 'delivery_date': '10/07/2019', 'qty': 100,
                     'val': 25000, 'credit_tenure': 20, 'maturity_date': '30/07/2019'}
                ]
            }
        }

        return report_data
