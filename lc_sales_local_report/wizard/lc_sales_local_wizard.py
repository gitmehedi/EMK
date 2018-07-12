from odoo import api, exceptions, fields, models, _


class LocalFirstAcceptanceWizard(models.TransientModel):
    _name = 'local.first.acceptance.wizard'

    product_temp_id = fields.Many2one('product.template', string='Product',required=True)

    @api.multi
    def report_print(self):

        data = {}
        data['product_temp_id'] = self.product_temp_id.id
        data['product_temp_name'] = self.product_temp_id.name

        return self.env['report'].get_action(self, 'lc_sales_local_report.local_first_acceptance_temp',
                                             data=data)

class LCSalesMaturityWizard(models.TransientModel):
    _name = 'lc.sales.maturity.wizard'

    product_temp_id = fields.Many2one('product.template', string='Product',required=True)

    @api.multi
    def report_print(self):

        data = {}
        data['product_temp_id'] = self.product_temp_id.id
        data['product_temp_name'] = self.product_temp_id.name

        return self.env['report'].get_action(self, 'lc_sales_local_report.lc_sales_maturity_temp',
                                             data=data)