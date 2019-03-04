from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _name = 'payment.instruction'
    _description = 'Payment Instruction'

    invoice_id = fields.Many2one('account.invoice',string="Invoice",copy=False)
    instruction_date = fields.Date(string='Date')
    amount = fields.Float(string='Amount')
    partner_id = fields.Many2one('res.partner', related='invoice_id.partner_id', string='Vendor')
    default_debit_account_id = fields.Many2one('account.account',related='invoice_id.partner_id.property_account_payable_id',
                                               string='Debit Account',store=True,
                                               help='Default Debit Account of the Payment')
    default_credit_account_id = fields.Many2one('account.account',related='invoice_id.partner_id.property_account_receivable_id',
                                                string='Credit Account',store=True,
                                                help='Default Credit Account of the Payment')
    is_sync = fields.Boolean(string='Is Synced', default=False)