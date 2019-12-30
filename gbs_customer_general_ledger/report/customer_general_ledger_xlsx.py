from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class CustomerGeneralLedgerXLSX(ReportXlsx):

    def _get_account_move_entry(self, accounts, init_balance, display_account, used_context):
        cr = self.env.cr
        aml_obj = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = aml_obj.with_context(used_context, date_from=used_context['date_from'], date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Opening Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                        '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                        NULL AS currency_id,\
                        '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                        '' AS partner_name\
                        FROM account_move_line l\
                        LEFT JOIN account_move m ON (l.move_id=m.id)\
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                        LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                        JOIN account_journal j ON (l.journal_id=j.id)\
                        WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = aml_obj.with_context(used_context)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res

    def generate_xlsx_report(self, workbook, data, obj):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        accounts = docs.property_account_receivable_id
        display_account = obj.display_account
        journal_ids = self.env['account.journal'].search([])
        init_balance = True

        # create context dictionary
        used_context = {}
        used_context['journal_ids'] = journal_ids.ids or False
        used_context['state'] = obj.target_move
        used_context['date_from'] = obj.date_from or False
        used_context['date_to'] = obj.date_to or False
        used_context['display_account'] = obj.display_account
        used_context['operating_unit_ids'] = False
        used_context['strict_range'] = True if obj.date_from else False
        used_context['lang'] = self.env.context.get('lang') or 'en_US'

        # get result data
        accounts_result = self._get_account_move_entry(accounts, init_balance, display_account, used_context)

        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        font_10 = workbook.add_format({'size': 10})
        font_12 = workbook.add_format({'bold': True, 'size': 12})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

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
        sheet = workbook.add_worksheet('General Ledger')

        # SET CELL WIDTH
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)

        # SHEET HEADER
        sheet.merge_range('A1:G6', '', center)
        sheet.write_rich_string('A1', font_12, docs.company_id.name, '\n', font_10, docs.company_id.street, '\n',
                                font_10, docs.company_id.street2, '\n', font_10, docs.company_id.city + '-' + docs.company_id.zip, '\n\n',
                                font_12, docs.name, bold, '\n Date: ', font_10, obj.date_from + ' To ' + obj.date_to, center)

        # TABLE HEADER
        row, col = 7, 0
        sheet.write(row, col, 'Date', th_cell_center)
        sheet.write(row, col + 1, 'Particulars', th_cell_center)
        sheet.write(row, col + 2, 'Ref', th_cell_center)
        sheet.write(row, col + 3, 'Debit', th_cell_center)
        sheet.write(row, col + 4, 'Credit', th_cell_center)
        sheet.write(row, col + 5, 'Balance', th_cell_center)
        sheet.write(row, col + 6, 'Currency', th_cell_center)

        # TABLE BODY
        row += 1
        for account in accounts_result:
            for rec in account['move_lines']:
                currency_format = workbook.add_format({'num_format': '#,###0.00' + ' ' + rec['currency_code'], 'size': 10, 'border': 1}) if rec['amount_currency'] > 0 else no_format
                amount_currency = rec['amount_currency'] if rec['amount_currency'] > 0 else ''

                if init_balance and rec['lname'] == 'Opening Balance':
                    sheet.merge_range(row, col, row, col + 2, rec['lname'], td_cell_center_bold)
                    sheet.write(row, col + 3, rec['debit'], total_format)
                    sheet.write(row, col + 4, rec['credit'], total_format)
                    sheet.write(row, col + 5, rec['balance'], total_format)
                    sheet.write(row, col + 6, amount_currency, currency_format)
                    row += 1
                else:
                    sheet.write(row, col, rec['ldate'], td_cell_center)
                    sheet.write(row, col + 1, rec['lname'], td_cell_left)
                    sheet.write(row, col + 2, rec['move_name'], td_cell_left)
                    sheet.write(row, col + 3, rec['debit'], no_format)
                    sheet.write(row, col + 4, rec['credit'], no_format)
                    sheet.write(row, col + 5, rec['balance'], no_format)
                    sheet.write(row, col + 6, amount_currency, currency_format)
                    row += 1

            sheet.merge_range(row, col, row, col + 2, 'Closing Balance', td_cell_center_bold)
            sheet.write(row, col + 3, account['debit'], total_format)
            sheet.write(row, col + 4, account['credit'], total_format)
            sheet.write(row, col + 5, account['balance'], total_format)
            sheet.write(row, col + 6, '', total_format)
            row += 1


CustomerGeneralLedgerXLSX('report.gbs_customer_general_ledger.customer_general_ledger_xlsx', 'customer.general.ledger.wizard', parser=report_sxw.rml_parse)
