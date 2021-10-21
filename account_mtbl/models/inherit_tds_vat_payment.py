from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class TDSVATPayment(models.Model):
    _inherit = 'tds.vat.payment'

    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit Sequence', readonly=True,
                                                   track_visibility='onchange', states={'draft': [('readonly', False)]})

    def _generate_credit_move_line(self, date, account_move_id, account_move_line_obj):
        account_move_line_credit = {
            'account_id': self.credit_account_id.id,
            'credit': round(self.amount, 2),
            'date_maturity': date,
            'debit': 0.0,
            'name': '/',
            'operating_unit_id': self.operating_unit_id.id,
            'move_id': account_move_id,
            'sub_operating_unit_id': self.credit_sub_operating_unit_id.id
        }
        return (0, 0, account_move_line_credit)

    def _generate_debit_move_line(self, line, date, account_move_id, account_move_line_obj):
        account_move_line_debit = {
            'account_id': line.account_id.id,
            'credit': 0.0,
            'date_maturity': date,
            'debit': round(line.credit, 2),
            'name': 'challan/' + line.name,
            'operating_unit_id': line.operating_unit_id.id,
            'move_id': account_move_id,
            'product_id': line.product_id.id or False,
            'sub_operating_unit_id': line.sub_operating_unit_id.id
        }
        return (0, 0, account_move_line_debit)
