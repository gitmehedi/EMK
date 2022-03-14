# imports of python library
import datetime

# imports of odoo
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class ChequePrintWizard(models.TransientModel):
    _name = "cheque.print.wizard"

    def _get_pay_to(self):
        pay_to = 'Cash'
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        if model == 'account.move':
            if docs.line_ids[0].partner_id:
                pay_to = docs.line_ids[0].partner_id.name
        else:
            pay_to = docs.partner_id.name

        return pay_to

    @api.model
    def _default_pay_to(self):
        return self._get_pay_to()

    @api.model
    def _default_date_on_cheque(self):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        if model == 'account.move':
            date_on_cheque = docs.date
        else:
            date_on_cheque = docs.payment_date

        return date_on_cheque

    @api.model
    def _default_amount(self):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        account_type_obj = self.env['account.account.type'].suspend_security().search([('is_bank_type', '=', True)],
                                                                                      limit=1, order="id asc")
        credit_amount = 0

        for line in docs.line_ids:
            if line.account_id.user_type_id == account_type_obj.id:
                credit_amount = line.credit
        return credit_amount

    pay_to = fields.Char("Pay To", required=True, default=_default_pay_to)
    is_cross_cheque = fields.Boolean(string='Is Cross Cheque')
    date_on_cheque = fields.Date("Date On Cheque", required=True, default=_default_date_on_cheque)
    amount = fields.Float("Amount", required=True, default=_default_amount)
    amount_in_word = fields.Char("Amount In Word", required=True)
    # reference = fields.Char("Reference")

    @api.onchange('amount')
    def _onchange_amount(self):
        if self.amount:
            self.amount_in_word = self.env['res.currency'].amount_to_word(float(self.amount), False) + ' Only'

    # @api.onchange('is_cross_cheque')
    # def _onchange_is_cross_cheque(self):
    #     if self.is_cross_cheque:
    #         self.pay_to = 'Cash'
    #     else:
    #         self.pay_to = self._get_pay_to()
    
    @api.multi
    def button_print_pdf(self):
        data = dict()
        data['pay_to'] = self.pay_to
        data['date_on_cheque'] = self.date_on_cheque
        data['amount'] = self.amount
        data['amount_in_word'] = self.amount_in_word
        data['company_name'] = self.env.user.company_id.name
        data['is_cross_cheque'] = self.is_cross_cheque


        return self.env['report'].get_action(self, 'gbs_cheque_management.report_cheque_print', data=data)

    @api.multi
    def button_print_on_printer(self):
        print ('hi printer')
