from odoo import models, fields, api, _


class TDSVATMovePaymentWizard(models.TransientModel):
    _name = 'tds.vat.move.payment.wizard'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Float(string='Amount', required=True, readonly=True,
                          default=lambda self: self.env.context.get('total_amount'))
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        required=True)
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today,
                                   required=True, copy=False)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    # sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', required=True)

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
        })
        if move_lines:
            move_lines.write({'pending_for_paid': True})
        return {'type': 'ir.actions.act_window_close'}
