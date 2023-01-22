from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TDSVATMovePaymentWizard(models.TransientModel):
    _inherit = 'tds.vat.move.payment.wizard'

    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', required=True)
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        required=True, domain=[('gl_type','=','online')])
    instruction_date = fields.Date(string='Date', default=lambda self:self.env.user.company_id.batch_date,
                                   required=True, copy=False)

    @api.constrains('credit_account_id')
    def _check_credit_account_id(self):
        if self.credit_account_id and self.credit_account_id.gl_type != 'online':
            raise ValidationError('Please select appropriate GL')

    @api.onchange('credit_account_id')
    def _onchange_credit_account_id(self):
        for rec in self:
            rec.credit_sub_operating_unit_id = None

    @api.multi
    def action_validate(self):

        if self.env.context.get('records'):
            move_lines = self.env['account.move.line'].search([('id', 'in', self.env.context.get('records'))])
        else:
            move_lines = False

        self.env['tds.vat.payment'].create({
            'currency_id': self.currency_id.id,
            'credit_account_id': self.credit_account_id.id,
            'amount': self.amount,
            'date': self.instruction_date,
            'operating_unit_id': self.operating_unit_id.id or None,
            'account_move_line_ids': [(6, 0, move_lines.ids)],
            'credit_sub_operating_unit_id': self.credit_sub_operating_unit_id.id or None
        })
        if move_lines:
            move_lines.write({'pending_for_paid': True})
        return {'type': 'ir.actions.act_window_close'}
