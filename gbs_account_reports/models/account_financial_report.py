from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.addons.account_reports.models.account_financial_report import FormulaLine, FormulaContext


class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    def _eval_formula(self, financial_report, debit_credit, context, currency_table, linesDict):
        debit_credit = debit_credit and financial_report.debit_credit
        formulas = self._split_formulas()
        if self.code and self.code in linesDict:
            res = linesDict[self.code]
        else:
            res = FormulaLine(self.with_context(operating_unit_ids=context.operating_unit_ids.ids), currency_table, financial_report, linesDict=linesDict)
        vals = {}
        vals['balance'] = res.balance
        if debit_credit:
            vals['credit'] = res.credit
            vals['debit'] = res.debit

        results = {}
        if self.domain and self.groupby and self.show_domain != 'never':
            aml_obj = self.env['account.move.line']
            tables, where_clause, where_params = aml_obj.with_context(operating_unit_ids=context.operating_unit_ids.ids)._query_get(domain=safe_eval(self.domain))
            sql, params = self._get_with_statement(financial_report)
            if financial_report.tax_report:
                where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

            groupby = self.groupby or 'id'
            if groupby not in self.env['account.move.line']:
                raise ValueError('Groupby should be a field from account.move.line')
            select, select_params = self._query_get_select_sum(currency_table)
            params += select_params
            sql = sql + "SELECT \"account_move_line\"." + groupby + ", " + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY \"account_move_line\"." + groupby

            params += where_params
            self.env.cr.execute(sql, params)
            results = self.env.cr.fetchall()
            results = dict([(k[0], {'balance': k[1], 'amount_residual': k[2], 'debit': k[3], 'credit': k[4]}) for k in results])
            c = FormulaContext(self.env['account.financial.html.report.line'], linesDict, currency_table, financial_report, only_sum=True)
            if formulas:
                for key in results:
                    c['sum'] = FormulaLine(results[key], currency_table, financial_report, type='not_computed')
                    c['sum_if_pos'] = FormulaLine(results[key]['balance'] >= 0.0 and results[key] or {'balance': 0.0}, currency_table, financial_report, type='not_computed')
                    c['sum_if_neg'] = FormulaLine(results[key]['balance'] <= 0.0 and results[key] or {'balance': 0.0}, currency_table, financial_report, type='not_computed')
                    for col, formula in formulas.items():
                        if col in results[key]:
                            results[key][col] = safe_eval(formula, c, nocopy=True)
            to_del = []
            for key in results:
                if self.env.user.company_id.currency_id.is_zero(results[key]['balance']):
                    to_del.append(key)
            for key in to_del:
                del results[key]

        results.update({'line': vals})
        return results
