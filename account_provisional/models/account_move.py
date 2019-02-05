from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"


    def action_create_provisional_journal(self):
        # acc_inv_line_objs = self.env['account.invoice.line'].read_group([('product_id.is_provisional_expense','=',True)],
        #                                                                 ['price_subtotal_without_vat','operating_unit_id'],
        #                                                                 groupby=['operating_unit_id'])
        acc_inv_line_objs = self.env['account.invoice.line'].search([('product_id.is_provisional_expense','=',True)])
        acc_journal_objs = self.env['account.journal'].search([('type','=','provisional')])

        for acc_inv_line_obj in acc_inv_line_objs:
            self._generate_move(acc_journal_objs,acc_inv_line_obj.operating_unit_id,acc_inv_line_obj.price_subtotal_without_vat)
        return True

    def _generate_move(self, journal,operating_unit_id,amount):
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        date = fields.Date.context_today(self)
        name = journal.with_context(ir_sequence_date=date).sequence_id.next_by_id()

        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        account_move_id = False
        if not account_move_id:
            account_move_dict = {
                'name': name,
                'date': date,
                'ref': '',
                'company_id': operating_unit_id.partner_id.id,
                'journal_id': journal.id,
                'operating_unit_id': operating_unit_id.id,
            }
            account_move = account_move_obj.create(account_move_dict)
            if account_move:
                account_move_id = account_move.id


                account_move_line_credit = {
                    'account_id': journal.default_credit_account_id.id,
                    # 'analytic_account_id': self.invoice_line_ids[0].account_analytic_id.id,
                    'credit': amount,
                    'date_maturity': date,
                    'debit': False,
                    # 'invoice_id': self.id,
                    'name': '/',
                    'operating_unit_id': operating_unit_id.id,
                    # 'partner_id': self.partner_id.id,
                    'move_id': account_move_id,
                }
                account_move_line_obj.create(account_move_line_credit)
                account_move_line_debit = {
                    'account_id': journal.default_debit_account_id.id,
                    # 'analytic_account_id': self.invoice_line_ids[0].account_analytic_id.id,
                    'credit': False,
                    'date_maturity': date,
                    'debit': amount,
                    # 'invoice_id': self.id,
                    'name': '/',
                    'operating_unit_id': operating_unit_id.id,
                    # 'partner_id': self.partner_id.id,
                    'move_id': account_move_id,
                }
                account_move_line_obj.create(account_move_line_debit)
        return True

    def get_credit_move_line_vals(self):

        return True

    def get_debit_move_line_vals(self):

        return True

    def action_reverse_provisional_journal(self):
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
