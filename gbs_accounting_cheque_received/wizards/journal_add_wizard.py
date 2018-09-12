from odoo import models, fields, api


class JournalAddingWizard(models.TransientModel):
    _name = 'journal.adding.wizard'

    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', '=', 'bank')],required=True)

    @api.one
    def update_payment_journal_to_cheque_received(self, context=None):
        if context['active_id']:
            cheque_rcv_pool = self.env['accounting.cheque.received'].search([('id', '=', context['active_id'])])

            if cheque_rcv_pool.journal_id.currency_id:
                currency = cheque_rcv_pool.journal_id.currency_id
            else:
                currency = cheque_rcv_pool.company_id.currency_id

            cheque_rcv_pool.write({'currency_id':currency.id, 'journal_id': self.journal_id.id})

