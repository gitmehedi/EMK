from odoo import api, models, fields
from odoo.tools.misc import formatLang


class YearlySalesComparisonReport(models.AbstractModel):
    _name = "report.samuda_sales_report.report_yearly_sales_comparison"

    sql_str = """"""

    @api.multi
    def render_html(self, docids, data=None):
        products = self.env['product.template'].search([('sale_ok', '=', 1), ('active', '=', 1)], order='id ASC')
        months = [{'sl': 1, 'name': 'Jan'}, {'sl': 2, 'name': 'Feb'}, {'sl': 3, 'name': 'Mar'},
                  {'sl': 4, 'name': 'Apr'}, {'sl': 5, 'name': 'May'}, {'sl': 6, 'name': 'Jun'},
                  {'sl': 7, 'name': 'Jul'}, {'sl': 8, 'name': 'Aug'}, {'sl': 9, 'name': 'Sep'},
                  {'sl': 10, 'name': 'Oct'}, {'sl': 11, 'name': 'Nov'}, {'sl': 12, 'name': 'Dec'}]
        # data type dictionary
        report_data = self.get_data(data, months)
        docargs = {
            'data': data,
            'header_data': months,
            'report_data': report_data,
            'formatLang': self.format_lang,
        }

        return self.env['report'].render('samuda_sales_report.report_yearly_sales_comparison', docargs)

    @api.multi
    def format_lang(self, value):
        return formatLang(self.env, value)

    @api.model
    def get_data(self, data, months):
        # Default report data
        report_data = {
            2018: {
                'year': 2018,
                'products': {
                    0: {
                        'product_name': 'Test Product',
                        'months': {
                            m['sl']: {
                                'qty': 100,
                                'val': 200
                            }
                            for m in months
                        }
                    },
                    1: {
                        'product_name': 'Own Product',
                        'months': {
                            m['sl']: {
                                'qty': 50,
                                'val': 100
                            }
                            for m in months
                        }
                    }
                }
            },
            2019: {
                'year': 2019,
                'products': {
                    0: {
                        'product_name': 'Test Product',
                        'months': {
                            m['sl']: {
                                'qty': 300,
                                'val': 500
                            }
                            for m in months
                        }
                    },
                    1: {
                        'product_name': 'Own Product',
                        'months': {
                            m['sl']: {
                                'qty': 150,
                                'val': 250
                            }
                            for m in months
                        }
                    }
                }
            }
        }

        return report_data
