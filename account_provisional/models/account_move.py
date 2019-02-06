from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"


    def action_create_provisional_journal(self):
        # todo need to add date range query
        acc_inv_line_objs = self.env['account.invoice.line'].search([('product_id.is_provisional_expense','=',True)], order='operating_unit_id asc')
        acc_journal_objs = self.env['account.journal'].search([('type','=','provisional')])
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        op_unit_list = []
        acc_inv_line_grp_list = []
        date = fields.Date.context_today(self)

        for acc_inv_line_obj in acc_inv_line_objs:
            value = acc_inv_line_obj.operating_unit_id.id
            if op_unit_list and op_unit_list[-1][0] == value:
                op_unit_list[-1].append(value)
                acc_inv_line_grp_list[-1].append(acc_inv_line_obj)
            else:
                op_unit_list.append([value])
                acc_inv_line_grp_list.append([acc_inv_line_obj])

        for acc_inv_line_obj_list in acc_inv_line_grp_list:
            move_obj = self._generate_move(acc_journal_objs, acc_inv_line_obj_list[0],
                                           date,account_move_obj)
            for acc_inv_line_obj in acc_inv_line_obj_list:
                self._generate_debit_move_line(acc_inv_line_obj, date, move_obj.id,account_move_line_obj)
                self._generate_credit_move_line(acc_journal_objs,acc_inv_line_obj,date,move_obj.id,account_move_line_obj)

            move_obj.post()
        return True

    def _generate_move(self, journal,acc_inv_line_obj_list,date,account_move_obj):
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)

        name = journal.with_context(ir_sequence_date=date).sequence_id.next_by_id()
        account_move_id = False
        if not account_move_id:
            account_move_dict = {
                'name': name,
                'date': date,
                'ref': '',
                'company_id': acc_inv_line_obj_list.company_id.id,
                'journal_id': journal.id,
                'operating_unit_id': acc_inv_line_obj_list.operating_unit_id.id,
            }
            account_move = account_move_obj.create(account_move_dict)
        return account_move

    def _generate_credit_move_line(self,journal,acc_inv_line_obj,date,account_move_id,account_move_line_obj):
        account_move_line_credit = {
            'account_id': journal.default_credit_account_id.id,
            'analytic_account_id': acc_inv_line_obj.account_analytic_id.id,
            'credit': acc_inv_line_obj.price_subtotal,
            'date_maturity': date,
            'debit':  False,
            'name': '/',
            'operating_unit_id':  acc_inv_line_obj.operating_unit_id.id,
            'partner_id': acc_inv_line_obj.partner_id.id,
            'move_id': account_move_id,
        }
        account_move_line_obj.create(account_move_line_credit)
        return True

    def _generate_debit_move_line(self,acc_inv_line_obj,date,account_move_id,account_move_line_obj):
        account_move_line_debit = {
            'account_id': acc_inv_line_obj.account_id.id,
            'analytic_account_id': acc_inv_line_obj.account_analytic_id.id,
            'credit': False,
            'date_maturity': date,
            'debit':  acc_inv_line_obj.price_subtotal,
            'name': acc_inv_line_obj.name,
            'operating_unit_id':  acc_inv_line_obj.operating_unit_id.id,
            'partner_id': acc_inv_line_obj.partner_id.id,
            'move_id': account_move_id,
        }
        account_move_line_obj.create(account_move_line_debit)
        return True

    def action_reverse_provisional_journal(self):
        date = fields.Date.context_today(self)
        journal_id = self.env['account.journal'].search([('type','=','provisional')])
        # todo need to update date range query
        date_range_objs = self.env['date.range'].search([('date_end', '<', date),('type_name', '=', 'Account')],order='id DESC',limit=1)
        ac_move_ids = self.env['account.move'].search([('date', '<=', date_range_objs.date_end),('date', '>=', date_range_objs.date_start),
                                                       ('journal_id','=',journal_id)])
        res = self.env['account.move'].browse(ac_move_ids).reverse_moves(date, journal_id or False)
        return res
