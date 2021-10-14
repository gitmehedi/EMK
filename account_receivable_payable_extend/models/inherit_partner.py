import datetime
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _credit_debit_get(self):
        current_date_str = datetime.datetime.today().strftime('%Y-%m-%d')
        fy_date_start, _ = self._get_fiscal_year_date_range(current_date_str)

        tables, where_clause, where_params = self.env['account.move.line'].with_context(company_id=self.env.user.company_id.id)._query_get()
        where_clause += ' AND ("account_move_line"."date" <= %s AND "account_move_line"."date" >= %s)'
        where_params = [tuple(self.ids)] + where_params + [current_date_str, fy_date_start]
        if where_clause:
            where_clause = 'AND ' + where_clause

        self._cr.execute("""SELECT account_move_line.partner_id, act.type, SUM(account_move_line.amount_residual)
                          FROM account_move_line
                          LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                          LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
                          WHERE act.type IN ('receivable','payable')
                          AND account_move_line.partner_id IN %s
                          AND account_move_line.reconciled IS FALSE
                          """ + where_clause + """
                          GROUP BY account_move_line.partner_id, act.type
                          """, where_params)
        for pid, type, val in self._cr.fetchall():
            partner = self.browse(pid)
            if type == 'receivable':
                partner.credit = val
            elif type == 'payable':
                partner.debit = -val

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
