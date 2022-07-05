from odoo import fields, models, api, _


class InheritedChequePrintWizard(models.TransientModel):
    _inherit = "cheque.print.wizard"

    @api.multi
    def action_cancel(self):
        if self._context.get('from_payment'):
            from_payment = self._context['from_payment']
        else:
            from_payment = False

        view = self.env.ref('account.view_account_payment_invoice_form')
        if from_payment:
            return {
                'name': _('Register Payment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'context': {'default_invoice_ids': [(4, 95096, None)]},
                'view_id': [view.id],
                'nodestroy': True,
                'target': 'new'
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
