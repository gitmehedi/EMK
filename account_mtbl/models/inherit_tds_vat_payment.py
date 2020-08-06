from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class TDSVATPayment(models.Model):
    _inherit = 'tds.vat.payment'

    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit Sequence', readonly=True,
                                                   track_visibility='onchange', states={'draft': [('readonly', False)]})

    def _generate_credit_move_line(self, date, account_move_id, account_move_line_obj):
        account_move_line_credit = {
            'account_id': self.credit_account_id.id,
            'credit': self.amount,
            'date_maturity': date,
            'debit': False,
            'name': '/',
            'operating_unit_id': self.operating_unit_id.id,
            'move_id': account_move_id,
            'sub_operating_unit_id': self.credit_sub_operating_unit_id.id
        }
        account_move_line_obj.create(account_move_line_credit)
        return True

    def _generate_debit_move_line(self, line, date, account_move_id, account_move_line_obj):
        account_move_line_debit = {
            'account_id': line.account_id.id,
            # 'analytic_account_id': line.acc_move_line_id.analytic_account_id.id,
            'credit': False,
            'date_maturity': date,
            'debit': line.credit,
            'name': 'challan/' + line.name,
            'operating_unit_id': line.operating_unit_id.id,
            'move_id': account_move_id,
            'product_id': line.product_id.id or False,
            'sub_operating_unit_id': line.sub_operating_unit_id.id
            # 'partner_id': acc_inv_line_obj.partner_id.id,
        }
        account_move_line_obj.create(account_move_line_debit)
        return True


