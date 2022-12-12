from odoo import api, exceptions, fields, models, _


class LocalFirstAcceptanceWizard(models.TransientModel):
    _name = 'local.first.acceptance.wizard'

    product_temp_id = fields.Many2many('product.template', string='Product',required=True,
                                      domain=[('sale_ok', '=', True)])

    @api.multi
    def report_print(self):

        data = {}
        product = []
        for ou in self.product_temp_id:
            product.append(ou.name)
        data['product_temp_id'] = tuple(self.product_temp_id.ids)
        data['product_temp_name'] = product

        return self.env['report'].get_action(self, 'lc_sales_local_report.local_first_acceptance_temp',
                                             data=data)
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='hr_payroll_ot.top_sheet_department_xlsx')

    @api.multi
    def report_print_xls(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='lc_sales_local_report.lc_first_acceptance_report_xlsx')

class LocalSecondAcceptanceWizard(models.TransientModel):
    _name = 'local.second.acceptance.wizard'

    product_temp_id = fields.Many2many('product.template', string='Product',required=True,
                                      domain=[('sale_ok', '=', True)])

    @api.multi
    def report_print(self):
        data = {}
        product = []
        for ou in self.product_temp_id:
            product.append(ou.name)
        data['product_temp_id'] = tuple(self.product_temp_id.ids)
        data['product_temp_name'] = product

        return self.env['report'].get_action(self, 'lc_sales_local_report.local_second_acceptance_temp',
                                             data=data)

    @api.multi
    def report_print_xls(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='lc_sales_local_report.lc_second_acceptance_report_xlsx')

class LCSalesMaturityWizard(models.TransientModel):
    _name = 'lc.sales.maturity.wizard'

    product_temp_id = fields.Many2many('product.template', string='Product',required=True,
                                      domain = [('sale_ok', '=', True)])

    @api.multi
    def report_print(self):
        data = {}
        product = []
        for ou in self.product_temp_id:
            product.append(ou.name)
        data['product_temp_id'] = tuple(self.product_temp_id.ids)
        data['product_temp_name'] = product

        return self.env['report'].get_action(self, 'lc_sales_local_report.lc_sales_maturity_temp',
                                             data=data)

    @api.multi
    def report_print_xls(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='lc_sales_local_report.lc_local_maturity_report_xlsx')