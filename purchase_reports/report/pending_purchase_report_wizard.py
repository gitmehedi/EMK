from odoo import models, fields, api

class PendingPurchaseWizard(models.TransientModel):
    _name = "pending.purchase.wizard"

    type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign')
    ], string='Type')

    @api.multi
    def process_print(self):
        pur_type = self.env.context.get('type')

        data = {}
        if pur_type == 'local':
            data['purchase_name'] = 'Pending Local Purchase Report'
        else:
            data['purchase_name'] = 'Pending Foreign Purchase Report'


        return self.env['report'].get_action(self, 'purchase_reports.report_pending_purchase',data=data)
