from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = ["account.journal", "mail.thread"]

    name = fields.Char(string='Journal Name', required=True, track_visibility='onchange')
    code = fields.Char(string='Short Code', size=5, required=True, track_visibility='onchange',
                       help="The journal entries of this journal will be named using this prefix.")
    type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
    ], required=True, track_visibility='onchange',
        help="Select 'Sale' for customer invoices journals.\n" \
             "Select 'Purchase' for vendor bills journals.\n" \
             "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n" \
             "Select 'General' for miscellaneous operations journals.")

    default_credit_account_id = fields.Many2one('account.account', string='Default Credit Account',
                                                domain=[('deprecated', '=', False)], track_visibility='onchange',
                                                help="It acts as a default account for credit amount")
    default_debit_account_id = fields.Many2one('account.account', string='Default Debit Account',
                                               domain=[('deprecated', '=', False)], track_visibility='onchange',
                                               help="It acts as a default account for debit amount")
    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', track_visibility='onchange',
                                  help="This field contains the information related to the numbering of the journal entries of this journal.",
                                  required=True, copy=False)
    currency_id = fields.Many2one('res.currency', help='The currency used to enter statement', string="Currency",
                                  oldname='currency', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id, track_visibility='onchange',
                                 help="Company related to this journal")

    inbound_payment_method_ids = fields.Many2many('account.payment.method',
                                                  'account_journal_inbound_payment_method_rel', 'journal_id',
                                                  'inbound_payment_method',
                                                  domain=[('payment_type', '=', 'inbound')], string='Debit Methods',
                                                  default=lambda self: self._default_inbound_payment_methods(), track_visibility='onchange',
                                                  help="Means of payment for collecting money. Odoo modules offer various payments handling facilities, "
                                                       "but you can always use the 'Manual' payment method in order to manage payments outside of the software.")
    outbound_payment_method_ids = fields.Many2many('account.payment.method',
                                                   'account_journal_outbound_payment_method_rel', 'journal_id',
                                                   'outbound_payment_method',
                                                   domain=[('payment_type', '=', 'outbound')], string='Payment Methods',
                                                   default=lambda self: self._default_outbound_payment_methods(), track_visibility='onchange',
                                                   help="Means of payment for sending money. Odoo modules offer various payments handling facilities, "
                                                        "but you can always use the 'Manual' payment method in order to manage payments outside of the software.")

    # Bank journals fields
    display_on_footer = fields.Boolean("Show in Invoices Footer", track_visibility='onchange',
                                       help="Display this bank account on the footer of printed documents like invoices and sales orders.")
    bank_acc_number = fields.Char(related='bank_account_id.acc_number', track_visibility='onchange')
    bank_id = fields.Many2one('res.bank', related='bank_account_id.bank_id', track_visibility='onchange')
