from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _name = 'payment.instruction'
    _inherit = ["mail.thread",'ir.needaction_mixin']
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

    origin = fields.Char('Origin')

    state = fields.Selection([
        ('draft', "Draft"),
        ('approved', "Approved"),
        ('cancel', "Cancel"),
    ], default='draft', string="Status", track_visibility='onchange')


    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('payment.instruction.sequence') or ''
        return super(PaymentInstruction, self).create(vals)

    @api.multi
    def action_approve(self):
        return self.write({'state': 'approved'})

    @api.multi
    def action_reject(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def action_reset(self):
        return self.write({'state': 'draft'})
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]