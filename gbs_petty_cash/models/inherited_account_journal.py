from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang


class InheritedAccountJournal(models.Model):
    _inherit = 'account.journal'

    petty_cash_journal = fields.Boolean(default=False)

    @api.multi
    def cash_statements_action(self):
        action_name = self._context.get('action_name', False)
        if not action_name:
            if self.type == 'bank':
                action_name = 'action_view_bank_statement_tree_petty_cash'
            elif self.type == 'cash':
                action_name = 'action_view_bank_statement_tree_petty_cash'
            elif self.type == 'sale':
                action_name = 'action_invoice_tree1'
            elif self.type == 'purchase':
                action_name = 'action_invoice_tree2'
            else:
                action_name = 'action_move_journal_line'

        _journal_invoice_type_map = {
            ('sale', None): 'out_invoice',
            ('purchase', None): 'in_invoice',
            ('sale', 'refund'): 'out_refund',
            ('purchase', 'refund'): 'in_refund',
            ('bank', None): 'bank',
            ('cash', None): 'cash',
            ('general', None): 'general',
        }
        invoice_type = _journal_invoice_type_map[(self.type, self._context.get('invoice_type'))]

        ctx = self._context.copy()
        ctx.pop('group_by', None)
        ctx.update({
            'journal_type': self.type,
            'default_journal_id': self.id,
            'search_default_draft': 1,
        })

        [action] = self.env.ref('gbs_petty_cash.%s' % action_name).read()
        action['context'] = ctx
        # domain_ctx = self._context.get('use_domain', [])
        # domain_ctx.append({
        #     'journal_id': self.id
        # })
        action['domain'] = [('journal_id', '=', self.id)]
        if action_name in ['action_view_bank_statement_tree_petty_cash']:
            action['views'] = False
            action['view_id'] = False
        return action

    @api.multi
    def create_cash_statement_cash_in(self):
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id, 'default_journal_id': self.id, 'default_journal_type': 'cash',
                    'default_type_of_operation': 'cash_in'})
        return {
            'name': _('Create cash statement'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement',
            'context': ctx,
        }

    @api.multi
    def create_cash_statement_cash_out(self):
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id, 'default_journal_id': self.id, 'default_journal_type': 'cash',
                    'default_type_of_operation': 'cash_out'})
        return {
            'name': _('Create cash statement'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement',
            'context': ctx,
        }

    @api.multi
    def get_journal_dashboard_datas(self):
        currency = self.currency_id or self.company_id.currency_id
        number_to_reconcile = last_balance = account_sum = 0
        ac_bnk_stmt = []
        title = ''
        number_draft = number_waiting = number_late = 0
        sum_draft = sum_waiting = sum_late = 0.0

        ############################################################
        current_date_str = datetime.today().strftime('%Y-%m-%d')
        fy_date_start, temp = self._get_fiscal_year_date_range(current_date_str)

        ############################################################
        if self.type in ['bank', 'cash']:
            last_bank_stmt = self.env['account.bank.statement'].search([('journal_id', 'in', self.ids)],
                                                                       order="date desc, id desc", limit=1)
            last_balance = last_bank_stmt and last_bank_stmt[0].balance_end or 0
            # Get the number of items to reconcile for that bank journal
            self.env.cr.execute("""SELECT COUNT(DISTINCT(statement_line_id)) 
                           FROM account_move where statement_line_id 
                           IN (SELECT line.id 
                               FROM account_bank_statement_line AS line 
                               LEFT JOIN account_bank_statement AS st 
                               ON line.statement_id = st.id 
                               WHERE st.journal_id IN %s and st.state = 'open')""", (tuple(self.ids),))
            already_reconciled = self.env.cr.fetchone()[0]
            self.env.cr.execute("""SELECT COUNT(line.id) 
                               FROM account_bank_statement_line AS line 
                               LEFT JOIN account_bank_statement AS st 
                               ON line.statement_id = st.id 
                               WHERE st.journal_id IN %s and st.state = 'open'""", (tuple(self.ids),))
            all_lines = self.env.cr.fetchone()[0]
            number_to_reconcile = all_lines - already_reconciled
            # optimization to read sum of balance from account_move_line
            account_ids = tuple(filter(None, [self.default_debit_account_id.id, self.default_credit_account_id.id]))

            if account_ids:
                amount_field = 'balance' if (
                        not self.currency_id or self.currency_id == self.company_id.currency_id) else 'amount_currency'
                query = """SELECT sum(%s) FROM account_move_line WHERE account_id in %%s AND date <= %%s AND date >= %%s;""" % (
                    amount_field,)
                self.env.cr.execute(query, (account_ids, current_date_str, fy_date_start))
                query_results = self.env.cr.dictfetchall()
                if query_results and query_results[0].get('sum') != None:
                    account_sum = query_results[0].get('sum')
        # TODO need to check if all invoices are in the same currency than the journal!!!!
        elif self.type in ['sale', 'purchase']:
            title = _('Bills to pay') if self.type == 'purchase' else _('Invoices owed to you')
            # optimization to find total and sum of invoice that are in draft, open state
            query = """SELECT state, amount_total, currency_id AS currency, type FROM account_invoice WHERE journal_id = %s AND state NOT IN ('paid', 'cancel');"""
            self.env.cr.execute(query, (self.id,))
            query_results = self.env.cr.dictfetchall()
            today = datetime.today()
            query = """SELECT amount_total, currency_id AS currency, type FROM account_invoice WHERE journal_id = %s AND date < %s AND state = 'open';"""
            self.env.cr.execute(query, (self.id, today))
            late_query_results = self.env.cr.dictfetchall()
            for result in query_results:
                if result['type'] in ['in_refund', 'out_refund']:
                    factor = -1
                else:
                    factor = 1
                cur = self.env['res.currency'].browse(result.get('currency'))
                if result.get('state') in ['draft', 'proforma', 'proforma2']:
                    number_draft += 1
                    sum_draft += cur.compute(result.get('amount_total'), currency) * factor
                elif result.get('state') == 'open':
                    number_waiting += 1
                    sum_waiting += cur.compute(result.get('amount_total'), currency) * factor
            for result in late_query_results:
                if result['type'] in ['in_refund', 'out_refund']:
                    factor = -1
                else:
                    factor = 1
                cur = self.env['res.currency'].browse(result.get('currency'))
                number_late += 1
                sum_late += cur.compute(result.get('amount_total'), currency) * factor

        difference = currency.round(last_balance - account_sum) + 0.0
        found_opening_balance_entry = False
        starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)
        opening_move = self.env['account.move'].sudo().search(
            [('date', '=', starting_day_of_current_year), ('is_opening', '=', True)])
        if opening_move:
            found_opening_balance_entry = True
        return {
            'number_to_reconcile': number_to_reconcile,
            'account_balance': formatLang(self.env, currency.round(account_sum) + 0.0, currency_obj=currency),
            'last_balance': formatLang(self.env, currency.round(last_balance) + 0.0, currency_obj=currency),
            'difference': formatLang(self.env, difference, currency_obj=currency) if difference else False,
            'number_draft': number_draft,
            'number_waiting': number_waiting,
            'number_late': number_late,
            'sum_draft': formatLang(self.env, currency.round(sum_draft) + 0.0, currency_obj=currency),
            'sum_waiting': formatLang(self.env, currency.round(sum_waiting) + 0.0, currency_obj=currency),
            'sum_late': formatLang(self.env, currency.round(sum_late) + 0.0, currency_obj=currency),
            'currency_id': currency.id,
            'bank_statements_source': self.bank_statements_source,
            'title': title,
            'found_opening_balance_entry': found_opening_balance_entry,
        }

    @api.multi
    def _get_fiscal_year_date_range(self, date_from):
        cr = self.env.cr

        date_start, date_end = False, False

        sql = """SELECT dr.date_start, dr.date_end 
                     FROM date_range dr 
                     LEFT JOIN date_range_type drt ON drt.id = dr.type_id 
                     WHERE drt.fiscal_year = true AND dr.date_start <= %s AND dr.date_end >= %s"""

        cr.execute(sql, (date_from, date_from))

        for row in cr.dictfetchall():
            date_start = row['date_start']
            date_end = row['date_end']

        return date_start, date_end
