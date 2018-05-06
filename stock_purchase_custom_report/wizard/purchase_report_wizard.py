from odoo import api, exceptions, fields, models


class PurchaseReportWizard(models.TransientModel):
    _name = 'purchase.report.wizard'

    date_from = fields.Date("Date from")
    date_to = fields.Date("Date to")
    partner_id = fields.Many2one('res.partner', string='Supplier')

    @api.multi
    def report_print(self):

        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['partner_id'] = self.partner_id.id

        return self.env['report'].get_action(self, 'stock_purchase_custom_report.stock_report_template',
                                             data=data)