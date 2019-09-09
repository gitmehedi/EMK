# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTrialBalance(models.AbstractModel):
    _inherit = 'report.account.report_trialbalance'

    def _get_accounts(self, accounts, display_account):
        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters_init = filters
        where_params_init = where_params
        context = self.env.context
        if context['date_to']:
            filters_init = filters_init.replace('("account_move_line"."date" <= %s)  AND  ', '')
            del where_params_init[0]

        # compute the balance, debit and credit for the provided accounts
        if context['date_from']:
            request = "SELECT account_move_line.account_id AS id, SUM(account_move_line.debit) AS debit, SUM(account_move_line.credit) AS credit, (SUM(account_move_line.debit) - SUM(account_move_line.credit) + init.balance) AS balance," + \
                      "COALESCE(init.balance , 0) AS init_bal FROM " + tables + " account_move_line " + \
                      "JOIN ( SELECT account_id AS id,(SUM(debit) - SUM(credit)) AS balance FROM " + \
                      tables + " WHERE account_id IN %s " + filters_init + " GROUP BY account_id) init ON init.id= account_move_line.id " + \
                      "WHERE account_id IN %s " + filters + " GROUP BY account_id, init.balance"
            params = (tuple(accounts.ids),) + tuple(where_params) + (tuple(accounts.ids),) + tuple(where_params_init)
        else:
            request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance, 0  AS init_bal" + \
                    " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
            params = (tuple(accounts.ids),) + tuple(where_params)

        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['init_bal', 'credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result.keys():
                res['init_bal'] = account_result[account.id].get('init_bal')
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (
                    not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
                account_res.append(res)
        return account_res

    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }
        return self.env['report'].render('account.report_trialbalance', docargs)
