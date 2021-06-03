from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class AnalyticAccountXLSX(ReportXlsx):

    def _get_accounts(self, aml_obj, used_context):
        tables, where_clause, where_params = aml_obj.with_context(used_context)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = "".join(wheres)
        filters = filters.replace('account_move_line', 'l')
        sql = ('''SELECT DISTINCT l.account_id\
                    FROM account_move_line l\
                    JOIN account_move m ON (l.move_id=m.id)\
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    JOIN account_account acc ON (l.account_id = acc.id) \
                    WHERE ''' + filters)
        params = tuple(where_params)
        self.env.cr.execute(sql, params)

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

    def _get_account_move_entry(self, used_context):
        cr = self.env.cr
        aml_obj = self.env['account.move.line']
        accounts = self._get_accounts(aml_obj, used_context)
        if not accounts:
            return list()

        # OPENING BALANCE
        move_lines = dict(map(lambda x: (x, 0.0), accounts.ids))
        filters = " AND m.state='posted'" if used_context['state'] == 'posted' else ""
        fy_date_start, fy_date_end = self._get_fiscal_year_date_range(used_context['date_from'])
        opening_journal_ids = self.env['account.journal'].search([('type', '=', 'situation')])
        sql_of_opening_balance = """
                SELECT 
                    sub.account_id AS account_id, 
                    COALESCE(SUM(sub.debit),0) AS debit, 
                    COALESCE(SUM(sub.credit),0) AS credit, 
                    COALESCE(SUM(sub.debit),0) - COALESCE(SUM(sub.credit), 0) as balance
                FROM
                    ((SELECT
                        l.account_id AS account_id, 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance 
                    FROM account_move_line l
                        LEFT JOIN account_move m ON (l.move_id=m.id)
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)
                        LEFT JOIN account_invoice i ON (m.id =i.move_id)
                        JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE l.account_id IN %s AND l.date BETWEEN %s AND %s 
                        AND l.journal_id IN %s""" + filters + """ GROUP BY l.account_id)
                    UNION
                    (SELECT
                        l.account_id AS account_id, 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance
                    FROM account_move_line l 
                        LEFT JOIN account_move m ON (l.move_id=m.id)
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)
                        LEFT JOIN account_invoice i ON (m.id =i.move_id)
                        JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE l.account_id IN %s AND l.date < %s AND l.date >= %s AND l.journal_id IN %s
                            """ + filters + """ GROUP BY l.account_id)) AS sub
                GROUP BY sub.account_id"""

        params = (tuple(accounts.ids), fy_date_start, fy_date_end, tuple(opening_journal_ids.ids),
                  tuple(accounts.ids), used_context['date_from'], fy_date_start, tuple(used_context['journal_ids']))
        cr.execute(sql_of_opening_balance, params)

        for row in cr.dictfetchall():
            move_lines[row['account_id']] = row['balance']

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

        account_res = []
        for row in cr.dictfetchall():
            opening_balance = float(move_lines.get(row['account_id'], 0.0))
            closing_balance = opening_balance + float(row['balance'])
            row['opening_balance'] = opening_balance
            row['closing_balance'] = closing_balance
            account_res.append(row)

        return account_res

    def generate_xlsx_report(self, workbook, data, obj):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        journal_ids = self.env['account.journal'].search([('type', '!=', 'situation')])
        ou_name = obj.operating_unit_id.name if obj.operating_unit_id else 'All'
        cc_name = obj.cost_center_id.name if obj.cost_center_id else 'All'

        # create context dictionary
        used_context = {}
        used_context['journal_ids'] = journal_ids.ids or False
        used_context['state'] = 'all' if obj.all_entries else 'posted'
        used_context['date_from'] = obj.date_from
        used_context['date_to'] = obj.date_to
        used_context['operating_unit_ids'] = obj.operating_unit_id.ids or False
        used_context['cost_center_ids'] = obj.cost_center_id or False
        used_context['analytic_account_ids'] = docs or False
        used_context['strict_range'] = True if obj.date_from else False
        used_context['lang'] = self.env.context.get('lang') or 'en_US'

        # result data
        accounts_result = self._get_account_move_entry(used_context)

        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})

        # table header cell format
        th_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # table body cell format
        td_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'size': 10, 'border': 1})

        td_cell_center_bold = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # WORKSHEET
        sheet = workbook.add_worksheet('Analytic Report')

        # SET CELL WIDTH
        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 20)

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, 4, docs.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, 4, docs.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, 4, docs.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, 4, docs.company_id.city + '-' + docs.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, 4, "Analytic Report", name_format)
        sheet.merge_range(5, 0, 5, 1, "Operating Unit: " + ou_name, bold)
        sheet.merge_range(5, 3, 5, 4, "Cost Center: " + cc_name, bold)
        sheet.merge_range(6, 0, 6, 1, "Analytic Account: " + docs.name, bold)
        sheet.merge_range(6, 3, 6, 4, "Date: " + obj.date_from + " To " + obj.date_to, bold)

        # TABLE HEADER
        row, col = 8, 0
        sheet.write(row, col, 'Particulars', th_cell_center)
        sheet.write(row, col + 1, 'Opening Balance', th_cell_center)
        sheet.write(row, col + 2, 'Debit', th_cell_center)
        sheet.write(row, col + 3, 'Credit', th_cell_center)
        sheet.write(row, col + 4, 'Closing Balance', th_cell_center)

        # TABLE BODY
        row += 1
        for rec in accounts_result:
            sheet.write(row, col, rec['account_name'], td_cell_left)
            sheet.write(row, col + 1, rec['opening_balance'], no_format)
            sheet.write(row, col + 2, rec['debit'], no_format)
            sheet.write(row, col + 3, rec['credit'], no_format)
            sheet.write(row, col + 4, rec['closing_balance'], no_format)
            row += 1

        # GRAND TOTAL
        grand_total_of_opening_balance = sum(map(lambda x: x['opening_balance'], accounts_result))
        grand_total_of_debit = sum(map(lambda x: x['debit'], accounts_result))
        grand_total_of_credit = sum(map(lambda x: x['credit'], accounts_result))
        grand_total_of_closing_balance = sum(map(lambda x: x['closing_balance'], accounts_result))

        sheet.write(row, col, 'Grand Total', td_cell_center_bold)
        sheet.write(row, col + 1, grand_total_of_opening_balance, total_format)
        sheet.write(row, col + 2, grand_total_of_debit, total_format)
        sheet.write(row, col + 3, grand_total_of_credit, total_format)
        sheet.write(row, col + 4, grand_total_of_closing_balance, total_format)
        row += 1


AnalyticAccountXLSX('report.samuda_account_reports.analytic_account_xlsx', 'analytic.account.wizard', parser=report_sxw.rml_parse)
