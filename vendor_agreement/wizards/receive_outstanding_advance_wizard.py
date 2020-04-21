from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RecieveOutstandingAdvanceWizard(models.TransientModel):
    _name = 'receive.outstanding.advance.wizard'

    agreement_id = fields.Many2one('agreement', string='Agreement', readonly=True,
                                   default=lambda self: self.env.context.get('active_id'))
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    amount = fields.Float('Amount', required=True,
                          default=lambda self: self.env.context.get('amount'))
    debit_account_id = fields.Many2one('account.account', string='Debit Account')
    branch_id = fields.Many2one('operating.unit', string='Branch')
    sou_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit')

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            agreement_amount = self.env.context.get('amount')
            if line.amount > agreement_amount:
                raise ValidationError(_("Sorry! This amount is bigger then agreement balance. "
                                        "Remaining balance is %s") % (agreement_amount))

    @api.multi
    def action_confirm(self):

        self.env['receive.outstanding.advance'].create({
            'agreement_id': self.agreement_id.id,
            'amount': self.amount,
            'debit_account_id': self.debit_account_id.id,
            'currency_id': self.currency_id.id,
            'branch_id': self.branch_id.id if self.branch_id else None,
            'sou_id': self.sou_id.id if self.sou_id else None
        })
        return {'type': 'ir.actions.act_window_close'}