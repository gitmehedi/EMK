from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TDSVATMovePaymentWizard(models.TransientModel):
    _name = 'tds.vat.move.payment.wizard'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                   default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Float(string='Amount', required=True,readonly=True,
                          default=lambda self: self.env.context.get('total_amount'))
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        required=True)
    instruction_date = fields.Date(string='Date', default=fields.Date.context_today,
                                   required=True, copy=False)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    # sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit')

    @api.multi
    def action_validate(self):

        if self.env.context.get('records'):
            move_lines = self.env['account.move.line'].search([('id','in',self.env.context.get('records'))])
        else:
            move_lines = False

        self.env['tds.vat.payment'].create({
                'currency_id': self.currency_id.id,
                'credit_account_id': self.credit_account_id.id,
                'amount': self.amount,
                'date': self.instruction_date,
                'operating_unit_id': self.operating_unit_id.id or None,
                'account_move_line_ids':[(6, 0, move_lines.ids)],
            })
        if move_lines:
            move_lines.write({'pending_for_paid': True})
        return {'type': 'ir.actions.act_window_close'}


    # -----------------------------------------------------------------------------------
    #payment instruction
    # @api.onchange('operating_unit_id')
    # def _onchange_operating_unit_id(self):
    #     if self.operating_unit_id:
    #         sub_operating_unit_ids = self.env['sub.operating.unit'].search([('operating_unit_id','=',self.operating_unit_id.id)])
    #         if sub_operating_unit_ids:
    #             return {'domain': {
    #                 'sub_operating_unit_id': [('id', 'in', sub_operating_unit_ids.ids)]
    #             }}

    # @api.multi
    # def action_validate(self):
    #     account_config_pool = self.env.user.company_id
    #     if account_config_pool and account_config_pool.sundry_account_id:
    #         debit_acc_id = account_config_pool.sundry_account_id
    #     else:
    #         raise UserError(
    #             _("Account Settings are not properly set. "
    #               "Please contact your system administrator for assistance."))
    #
    #     if self.env.context.get('records'):
    #         move_lines = self.env['account.move.line'].search([('id','in',self.env.context.get('records'))])
    #     else:
    #         move_lines = False
    #
    #     self.env['payment.instruction'].create({
    #         'currency_id': self.currency_id.id,
    #         'default_debit_account_id': debit_acc_id and debit_acc_id.id or False,
    #         'default_credit_account_id': self.credit_account_id.id,
    #         'instruction_date': self.instruction_date,
    #         'amount': self.amount,
    #         'operating_unit_id': self.operating_unit_id.id or None,
    #         'is_tax': True,
    #         'account_move_line_ids':[(6, 0, move_lines.ids)]
    #         # 'sub_operating_unit_id': self.sub_operating_unit_id and self.sub_operating_unit_id.id or False,
    #     })
    #     if move_lines:
    #         move_lines.write({'pending_for_paid': True})
    #     return {'type': 'ir.actions.act_window_close'}
