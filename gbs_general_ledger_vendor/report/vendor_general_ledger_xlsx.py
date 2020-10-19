from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class VendorGeneralLedgerXLSX(ReportXlsx):

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

    def _get_account_move_entry(self, accounts, init_balance, display_account, used_context):
        cr = self.env.cr
        aml_obj = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))
        state = used_context['state']
        partner_id = used_context['partner_id']

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            fy_date_start, fy_date_end = self._get_fiscal_year_date_range(used_context['date_from'])
            journal_ids = self.env['account.journal'].search([('type', '=', 'situation')])
            init_balance_line = {'lid': 0, 'lpartner_id': '', 'account_id': accounts.ids[0], 'invoice_type': '',
                                 'invoice_id': '', 'currency_id': None, 'move_name': '', 'lname': 'Opening Balance',
                                 'debit': 0.0, 'credit': 0.0, 'balance': 0.0, 'mmove_id': '', 'partner_name': '',
                                 'currency_code': '', 'lref': '', 'amount_currency': None, 'invoice_number': '',
                                 'lcode': '', 'ldate': ''}

            # OPENING BALANCE
            sql = """SELECT 
                            l.account_id AS account_id, 
                            COALESCE(SUM(l.debit),0.0) AS debit, 
                            COALESCE(SUM(l.credit),0.0) AS credit, 
                            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance     
                        FROM 
                            account_move_line l
                            LEFT JOIN account_move m ON (l.move_id=m.id)
                            LEFT JOIN res_partner p ON (l.partner_id=p.id)
                            JOIN account_journal j ON (l.journal_id=j.id)
                        WHERE 
                            l.account_id IN %s AND l.partner_id=%s
                            AND l.date BETWEEN %s AND %s AND l.journal_id IN %s
            """

            sql += " AND m.state=%s GROUP BY l.account_id" if state == 'posted' else " GROUP BY l.account_id"

            if state == 'posted':
                params = (tuple(accounts.ids), partner_id, fy_date_start, fy_date_end, tuple(journal_ids.ids), state)
            else:
                params = (tuple(accounts.ids), partner_id, fy_date_start, fy_date_end, tuple(journal_ids.ids))

            cr.execute(sql, params)

            for row in cr.dictfetchall():
                init_balance_line['account_id'] = row['account_id']
                init_balance_line['debit'] = row['debit']
                init_balance_line['credit'] = row['credit']
                init_balance_line['balance'] = row['balance']

            # ADD BALANCE WITH OPENING BALANCE
            sql = """SELECT 
                            l.account_id AS account_id, 
                            COALESCE(SUM(l.debit),0.0) AS debit, 
                            COALESCE(SUM(l.credit),0.0) AS credit, 
                            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance     
                        FROM 
                            account_move_line l
                            LEFT JOIN account_move m ON (l.move_id=m.id)
                            LEFT JOIN res_currency c ON (l.currency_id=c.id)
                            LEFT JOIN res_partner p ON (l.partner_id=p.id)
                            LEFT JOIN account_invoice i ON (m.id =i.move_id)
                            JOIN account_journal j ON (l.journal_id=j.id)
                        WHERE 
                            l.account_id IN %s AND l.partner_id=%s 
                            AND l.date < %s AND l.date >= %s AND l.journal_id IN %s
            """

            sql += " AND m.state=%s GROUP BY l.account_id" if state == 'posted' else " GROUP BY l.account_id"

            if state == 'posted':
                params = (tuple(accounts.ids), partner_id, used_context['date_from'], fy_date_start, tuple(used_context['journal_ids']), state)
            else:
                params = (tuple(accounts.ids), partner_id, used_context['date_from'], fy_date_start, tuple(used_context['journal_ids']))

            cr.execute(sql, params)

            for row in cr.dictfetchall():
                init_balance_line['debit'] += row['debit']
                init_balance_line['credit'] += row['credit']
                init_balance_line['balance'] += row['balance']

            move_lines[init_balance_line.pop('account_id')].append(init_balance_line)

        sql_sort = 'l.date, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = aml_obj.with_context(used_context)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, invl.price_unit, invl.quantity AS qty, u.name AS unit_name, m.narration AS narration, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                    m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
                    FROM account_move_line l\
                    JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                    LEFT JOIN account_invoice_line invl ON (i.id=invl.invoice_id)\
                    LEFT JOIN product_uom u ON (invl.uom_id=u.id)\
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    JOIN account_account acc ON (l.account_id = acc.id) \
                    WHERE l.partner_id=%s AND l.account_id IN %s ''' + filters + ''' GROUP BY l.id, invl.price_unit, invl.quantity, u.name, m.narration, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)

        params = (partner_id, tuple(accounts.ids),) + tuple(where_params)
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
        accounts = docs.property_account_payable_id
        display_account = obj.display_account
        journal_ids = self.env['account.journal'].search([('type', '!=', 'situation')])
        init_balance = True

        # create context dictionary
        used_context = {}
        used_context['partner_id'] = docs.id
        used_context['journal_ids'] = journal_ids.ids or False
        used_context['state'] = obj.target_move
        used_context['date_from'] = obj.date_from or False
        used_context['date_to'] = obj.date_to or False
        used_context['display_account'] = obj.display_account
        used_context['operating_unit_ids'] = False
        used_context['strict_range'] = True if obj.date_from else False
        used_context['lang'] = self.env.context.get('lang') or 'en_US'

        # result data
        accounts_result = self._get_account_move_entry(accounts, init_balance, display_account, used_context)

        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        font_10 = workbook.add_format({'size': 10})
        font_12 = workbook.add_format({'bold': True, 'size': 12})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

        # EXCEL HEADER FORMAT
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
        sheet = workbook.add_worksheet('General Ledger')

        # SET CELL WIDTH
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 30)
        sheet.set_column('F:F', 13)
        sheet.set_column('G:G', 13)
        sheet.set_column('H:H', 13)

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, 7, docs.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, 7, docs.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, 7, docs.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, 7, docs.company_id.city + '-' + docs.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, 7, "Vendor General Ledger", name_format)
        sheet.merge_range(5, 0, 5, 2, "Vendor Name: " + docs.name, bold)
        sheet.merge_range(5, 5, 5, 7, "Date: " + obj.date_from + " To " + obj.date_to, font_10)

        # TABLE HEADER
        row, col = 7, 0
        sheet.write(row, col, 'Date', th_cell_center)
        sheet.write(row, col + 1, 'Type', th_cell_center)
        sheet.write(row, col + 2, 'Particulars', th_cell_center)
        sheet.write(row, col + 3, 'Ref', th_cell_center)
        sheet.write(row, col + 4, 'Explanation', th_cell_center)
        sheet.write(row, col + 5, 'Dr.', th_cell_center)
        sheet.write(row, col + 6, 'Cr.', th_cell_center)
        sheet.write(row, col + 7, 'Balance', th_cell_center)

        # TABLE BODY
        row += 1
        for account in accounts_result:
            for rec in account['move_lines']:
                if init_balance and rec['lname'] == 'Opening Balance':
                    sheet.merge_range(row, col, row, col + 4, rec['lname'], td_cell_center_bold)
                    sheet.write(row, col + 5, rec['debit'], total_format)
                    sheet.write(row, col + 6, rec['credit'], total_format)
                    sheet.write(row, col + 7, rec['balance'], total_format)
                    row += 1
                else:
                    journal_type = 'Vendor Payment' if rec['debit'] > 0 else 'Purchase'
                    sheet.write(row, col, rec['ldate'], td_cell_center)
                    sheet.write(row, col + 1, journal_type, td_cell_left)
                    sheet.write(row, col + 2, rec['lname'], td_cell_left)
                    sheet.write(row, col + 3, rec['move_name'], td_cell_left)
                    sheet.write(row, col + 4, rec['narration'], td_cell_left)
                    sheet.write(row, col + 5, rec['debit'], no_format)
                    sheet.write(row, col + 6, rec['credit'], no_format)
                    sheet.write(row, col + 7, rec['balance'], no_format)
                    row += 1

            sheet.merge_range(row, col, row, col + 4, 'Closing Balance', td_cell_center_bold)
            sheet.write(row, col + 5, account['debit'], total_format)
            sheet.write(row, col + 6, account['credit'], total_format)
            sheet.write(row, col + 7, account['balance'], total_format)
            row += 1


VendorGeneralLedgerXLSX('report.gbs_general_ledger_vendor.vendor_general_ledger_xlsx', 'vendor.general.ledger.wizard', parser=report_sxw.rml_parse)
