from odoo import fields, models, api


class AccountingReportUtility(models.TransientModel):
    _name = 'accounting.report.utility'

    def _get_accounts(self, date_start, date_end, analytic_account_ids):
        sql_str = """SELECT
                        DISTINCT aml.account_id
                    FROM
                        account_move_line aml
                        JOIN account_move am ON (aml.move_id=am.id)
                        JOIN account_account aa ON (aml.account_id = aa.id)
                    WHERE
                        aml.date BETWEEN %s AND %s
                        AND aml.analytic_account_id IN (%s)
        """
        params = (date_start, date_end, tuple(analytic_account_ids))
        self.env.cr.execute(sql_str, params)

        account_ids = [row['account_id'] for row in self.env.cr.dictfetchall()]
        accounts = self.env['account.account'].search([('id', 'in', account_ids)])

        return accounts

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

    def _get_account_move_entry(self, obj, used_context):
        cr = self.env.cr
        aml_obj = self.env['account.move.line']
        fy_date_start, fy_date_end = self._get_fiscal_year_date_range(used_context['date_from'])
        accounts = self._get_accounts(fy_date_start, fy_date_end, used_context['analytic_account_ids'].ids)
        if not accounts:
            return list()

        accounts_res = list(
            map(lambda x: {'account_id': x.id, 'account_name': x.name, 'opening_balance': 0.0, 'debit': 0.0,
                           'credit': 0.0, 'closing_balance': 0.0}, accounts))

        # OPENING BALANCE
        filters = " AND m.state='posted'" if used_context['state'] == 'posted' else ""
        filters += " AND l.analytic_account_id=%s" % used_context['analytic_account_ids'].id
        opening_journal_ids = self.env['account.journal'].search([('type', '=', 'situation')])
        sql_of_opening_balance = """
                SELECT 
                    sub.account_id AS account_id, 
                    sub.account_name,
                    0 AS debit, 
                    0 AS credit, 
                    COALESCE(SUM(sub.debit),0) - COALESCE(SUM(sub.credit), 0) AS balance
                FROM
                    ((SELECT
                        l.account_id AS account_id, 
                        acc.name AS account_name,
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit 
                    FROM account_move_line l
                        LEFT JOIN account_move m ON (l.move_id=m.id)
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)
                        LEFT JOIN account_invoice i ON (m.id =i.move_id)
                        JOIN account_journal j ON (l.journal_id=j.id)
                        JOIN account_account acc ON (l.account_id = acc.id)
                    WHERE l.account_id IN %s AND l.date BETWEEN %s AND %s 
                        AND l.journal_id IN %s""" + filters + """ GROUP BY l.account_id,acc.name)
                    UNION
                    (SELECT
                        l.account_id AS account_id, 
                        acc.name AS account_name,
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit
                    FROM account_move_line l 
                        LEFT JOIN account_move m ON (l.move_id=m.id)
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)
                        LEFT JOIN account_invoice i ON (m.id =i.move_id)
                        JOIN account_journal j ON (l.journal_id=j.id)
                        JOIN account_account acc ON (l.account_id = acc.id)
                    WHERE l.account_id IN %s AND l.date < %s AND l.date >= %s AND l.journal_id IN %s
                            """ + filters + """ GROUP BY l.account_id,acc.name)) AS sub
                GROUP BY sub.account_id,sub.account_name ORDER BY sub.account_id"""

        params = (tuple(accounts.ids), fy_date_start, fy_date_end, tuple(opening_journal_ids.ids),
                  tuple(accounts.ids), used_context['date_from'], fy_date_start, tuple(used_context['journal_ids']))
        cr.execute(sql_of_opening_balance, params)

        for row in cr.dictfetchall():
            line = filter(lambda l: l['account_id'] == row['account_id'], accounts_res)[0]
            line['opening_balance'] = row['balance']
            line['closing_balance'] = row['balance']

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = aml_obj.with_context(used_context)._query_get()


        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.account_id AS account_id, acc.name AS account_name, COALESCE(SUM(l.debit),0) AS debit, 
                    COALESCE(SUM(l.credit),0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance\
                    FROM account_move_line l\
                    JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    JOIN account_account acc ON (l.account_id = acc.id) \
                    WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.account_id, acc.name ORDER BY l.account_id''')
        params = (tuple(accounts.ids),) + tuple(where_params)

        cr.execute(sql, params)

        for row in cr.dictfetchall():
            line = filter(lambda l: l['account_id'] == row['account_id'], accounts_res)[0]
            line['debit'] = row['debit']
            line['credit'] = row['credit']
            line['closing_balance'] = line['closing_balance'] + row['balance']

        return accounts_res
