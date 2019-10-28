from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class PaymentInstruction(models.Model):
    _name = 'payment.instruction'
    _inherit = ["mail.thread", 'ir.needaction_mixin']
    _order = 'id desc'
    _rec_name = 'code'
    _description = 'Payment Instruction'

    sequence = fields.Integer('Sequence', track_visibility='onchange')
    code = fields.Char('Sequence', track_visibility='onchange')
    origin = fields.Char('Origin', track_visibility='onchange')
    instruction_date = fields.Date(string='Date', track_visibility='onchange')
    amount = fields.Float(string='Amount', track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='onchange')
    default_debit_account_id = fields.Many2one('account.account', string='Debit Account', track_visibility='onchange',
                                               required=True)
    debit_operating_unit_id = fields.Many2one('operating.unit', string='Debit Branch', track_visibility='onchange',
                                              required=True)
    debit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Debit SOU', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Vendor', track_visibility='onchange')
    vendor_bank_acc = fields.Char(string='Vendor Bank Account', track_visibility='onchange')
    default_credit_account_id = fields.Many2one('account.account', string='Credit Account', track_visibility='onchange')
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch', track_visibility='onchange')
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit SOU',
                                                   track_visibility='onchange')
    cbs_response = fields.Text('Response')
    is_sync = fields.Boolean(string='Payment Synced', default=False, track_visibility='onchange')
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    state = fields.Selection([('draft', "Draft"), ('approved', "Approved"), ('cancel', "Cancel"), ], default='draft',
                             string="Status", track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('payment.instruction.sequence') or ''
        return super(PaymentInstruction, self).create(vals)



    @api.multi
    def action_reject(self):
        if self.state == 'draft':
            return self.write({'state': 'cancel'})

    @api.multi
    def action_reset(self):
        if self.state == 'cancel':
            return self.write({'state': 'draft'})

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]
