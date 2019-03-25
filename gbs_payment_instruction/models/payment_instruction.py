from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _name = 'payment.instruction'
    _order='sequence desc'
    _description = 'Payment Instruction'


    sequence = fields.Integer('Sequence',help="Gives the sequence of this line when displaying the invoice.")
    instruction_date = fields.Date(string='Date')
    is_sync = fields.Boolean(string='Is Synced', default=False)
    amount = fields.Float(string='Amount')
    # relational fields
    partner_id = fields.Many2one('res.partner', string='Vendor')
    currency_id = fields.Many2one('res.currency', string='Currency')
    default_debit_account_id = fields.Many2one('account.account',string='Debit Account',
                                               help='Default Debit Account of the Payment')
    default_credit_account_id = fields.Many2one('account.account',string='Credit Account',
                                                help='Default Credit Account of the Payment')