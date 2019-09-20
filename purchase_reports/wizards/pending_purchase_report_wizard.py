from odoo import models, fields, api

class PendingPurchaseWizard(models.TransientModel):
    _name = "pending.purchase.wizard"

    type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign')
    ], string='Type')

    @api.multi
    def process_print(self):

        data = {}
        data['report_type'] = self.env.context.get('type')

        return self.env['report'].get_action(self, 'purchase_reports.report_pending_purchase',data=data)
