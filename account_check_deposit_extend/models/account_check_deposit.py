
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning as UserError


class AccountCheckEntry(models.Model):
    _inherit = "account.check.deposit"
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posting', 'Posting'),
        ('done', 'Done'),
        ], string='Status', default='draft', readonly=True)
                
    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, deposit, total_debit, total_amount_currency):
        return {
            'name': _('Check Deposit %s') % deposit.name,
            'debit': total_debit,
            'credit': 0.0,
#             'account_id': deposit.company_id.check_deposit_account_id.id,
            'account_id': deposit.partner_bank_id.journal_id.default_debit_account_id.id,
            'partner_id': False,
            'currency_id': deposit.currency_none_same_company_id.id or False,
            'amount_currency': total_amount_currency,
            }

    @api.multi
    def validate_posting(self):
        print ""
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        for deposit in self:
            for line in deposit.check_payment_ids:
                line.write({'is_postedtobank':True})
#
            deposit.write({'state': 'posting'})
        return True