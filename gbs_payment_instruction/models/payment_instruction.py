from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _name = 'payment.instruction'
    _inherit = "mail.thread"
    _order = 'id desc'
    _rec_name = 'code'
    _description = 'Payment Instruction'

    sequence = fields.Integer('Sequence', help="Gives the sequence of this line when displaying the invoice.")
    code = fields.Char('Sequence', help="Gives the sequence of this line when displaying the invoice.")
    instruction_date = fields.Date(string='Date')
    is_sync = fields.Boolean(string='Is Synced', default=False)
    amount = fields.Float(string='Amount')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    currency_id = fields.Many2one('res.currency', string='Currency')
    default_debit_account_id = fields.Many2one('account.account', string='Debit Account',
                                               help='Default Debit Account of the Payment')
    default_credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                                help='Default Credit Account of the Payment')
    vendor_bank_acc = fields.Char(string='Vendor Bank Account')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit')

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('payment.instruction.sequence') or ''
        return super(PaymentInstruction, self).create(vals)
