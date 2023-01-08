from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class AccountGeneralLedgerDetailsXLSX(ReportXlsx):

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

    def _get_account_move_entry(self, accounts, used_context):
        result_data_list = []
        cr = self.env.cr
        aml_obj = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))
        display_account = used_context['display_account']

        # OPENING BALANCE
        opening_balance_move_line = {
            'move_id': 0,
            'date': '',
            'journal_name': 'OC',
            'account_id': '',
            'account_code': '',
            'account_name': '',
            'operating_unit': '',
            'analytic_account_name': '',
            'department_name': '',
            'cost_center': '',
            'move_name': '',
            'reference': '',
            'entry_label': 'Opening Balance',
            'debit': 0.0,
            'credit': 0.0,
            'balance': 0.0
        }

        filters = " AND m.state='posted'" if used_context['state'] == 'posted' else ""
        if used_context['operating_unit_ids']:
            filters += " AND l.operating_unit_id IN (%s)" % tuple(used_context['operating_unit_ids'])

        fy_date_start, fy_date_end = self._get_fiscal_year_date_range(used_context['date_from'])
        opening_journal_ids = self.env['account.journal'].search([('type', '=', 'situation')])
        sql_of_opening_balance = """
                SELECT 
                    sub.account_id AS account_id, 
                    COALESCE(SUM(sub.debit),0.0) AS debit, 
                    COALESCE(SUM(sub.credit),0.0) AS credit, 
                    COALESCE(SUM(sub.debit),0) - COALESCE(SUM(sub.credit), 0) as balance
                FROM
                    ((SELECT
                        l.account_id AS account_id, 
                        COALESCE(SUM(l.debit),0.0) AS debit, 
                        COALESCE(SUM(l.credit),0.0) AS credit, 
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
                        COALESCE(SUM(l.debit),0.0) AS debit, 
                        COALESCE(SUM(l.credit),0.0) AS credit, 
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
            opening_balance_move_line['debit'] = row['debit']
            opening_balance_move_line['credit'] = row['credit']
            opening_balance_move_line['balance'] = row['balance']

        result_data_list.append(opening_balance_move_line)

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = aml_obj.with_context(used_context)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        sql_filters = ""
        if used_context['account_type_ids']:
            if len(used_context['account_type_ids']) > 1:
                sql_filters += """ AND acc.user_type_id IN %s""" % (tuple(used_context['account_type_ids']),)
            else:
                sql_filters += """ AND acc.user_type_id=%s""" % used_context['account_type_ids'][0]



        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT 
                        m.id AS move_id
                        ,l.id as line_id
                        ,m.narration
                        ,m.date
                        ,j.code AS journal_name
                        ,acc.id AS account_id
                        ,acc.code AS account_code
                        ,acc.name AS account_name
                        ,ou.name AS operating_unit
                        ,aaa.name AS analytic_account_name
                        ,d.name AS department_name
                        ,cc.name AS cost_center
                        ,m.ref AS reference
                        ,m.name AS move_name
                        ,l.name AS entry_label
                        ,COALESCE(l.debit,0) AS debit
                        ,COALESCE(l.credit,0) AS credit
                        ,COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance
                        ,CASE WHEN acc.id=%s THEN 1 ELSE 2 END AS sorting_col
                FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    JOIN account_account acc ON (l.account_id = acc.id)
                    JOIN account_account_type aat ON (aat.id=acc.user_type_id)
                    LEFT JOIN operating_unit ou ON (ou.id=l.operating_unit_id)
                    LEFT JOIN account_analytic_account aaa ON (aaa.id=l.analytic_account_id)
                    LEFT JOIN hr_department d ON (d.id=l.department_id)
                    LEFT JOIN account_cost_center cc ON (cc.id=l.cost_center_id)
                WHERE m.id IN (SELECT m.id 
                                FROM account_move_line l 
                                JOIN account_move m ON m.id=l.move_id 
                                WHERE l.account_id=%s ''' + filters + ''')
                    ''' + sql_filters + '''
                GROUP BY 
                     m.id
                     ,l.id
                     ,m.narration
                    ,m.date
                    ,j.code
                    ,acc.id
                    ,acc.code
                    ,acc.name
                    ,ou.name
                    ,aaa.name
                    ,d.name
                    ,cc.name
                    ,m.ref
                    ,m.name
                    ,l.name
                    ,l.debit
                    ,l.credit
                ORDER BY 
                    m.date, m.id, sorting_col''')

        params = (accounts.id, accounts.id) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            result_data_list.append(row)

        return result_data_list

    def generate_xlsx_report(self, workbook, data, obj):
        ReportUtility = self.env['report.utility']

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        journal_ids = self.env['account.journal'].search([('type', '!=', 'situation')])

        # create context dictionary
        used_context = {}
        used_context['journal_ids'] = journal_ids.ids or False
        used_context['state'] = obj.target_move
        used_context['date_from'] = obj.date_from or False
        used_context['date_to'] = obj.date_to or False
        used_context['display_account'] = obj.display_account
        used_context['strict_range'] = True if obj.date_from else False
        used_context['lang'] = self.env.context.get('lang') or 'en_US'
        used_context['operating_unit_ids'] = obj.operating_unit_id.ids or False
        used_context['account_type_ids'] = obj.account_type_ids.ids or False

        # result data
        accounts_result = self._get_account_move_entry(docs, used_context)

        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})
        narration_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10,  'bg_color' : '#f4e4d4'})

        # table header cell format
        th_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1, 'bg_color': '#78B0DE'})
        th_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # table body cell format
        td_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'size': 10, 'border': 1})

        td_cell_center_bold = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})


        td_cell_center_color = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1, 'bg_color': '#d4e4f4'})
        td_cell_left_color = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1, 'bg_color': '#d4e4f4'})
        no_format_color = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1, 'bg_color': '#d4e4f4'})

        # WORKSHEET
        sheet = workbook.add_worksheet('General Ledger Details')

        # SET CELL WIDTH
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 10)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 18)
        sheet.set_column(5, 5, 22)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 20)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)
        sheet.set_column(11, 11, 15)
        sheet.set_column(12, 12, 15)
        sheet.set_column(13, 13, 15)
        sheet.set_column(14, 14, 15)


        # SHEET HEADER
        sheet.merge_range(0, 0, 0, 13, docs.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, 13, docs.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, 13, docs.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, 13, docs.company_id.city + '-' + docs.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, 13, "General Ledger Details", name_format)
        sheet.merge_range(5, 0, 5, 4, "Account: " + docs.code + " " + docs.name, bold)
        sheet.merge_range(5, 11, 5, 13, "Date: " + ReportUtility.get_date_from_string(obj.date_from) + " To " + ReportUtility.get_date_from_string(obj.date_to), bold)
        if obj.operating_unit_id:
            sheet.merge_range(5, 8, 5, 9, "Operating Unit: " + obj.operating_unit_id.code, bold)

        # TABLE HEADER
        row, col = 7, 0
        sheet.write(row, col, 'Date', th_cell_center)
        sheet.write(row, col + 1, 'JRNL', th_cell_center)
        sheet.write(row, col + 2, 'GL Code', th_cell_center)
        sheet.write(row, col + 3, 'GL Name', th_cell_center)
        sheet.write(row, col + 4, 'Analytic Account', th_cell_center)
        sheet.write(row, col + 5, 'Operating Unit', th_cell_center)
        sheet.write(row, col + 6, 'Department', th_cell_center)
        sheet.write(row, col + 7, 'Cost Center', th_cell_center)
        sheet.write(row, col + 8, 'Ref', th_cell_center)
        sheet.write(row, col + 9, 'Move', th_cell_center)
        sheet.write(row, col + 10, 'Entry Label', th_cell_center)
        sheet.write(row, col + 11, 'Debit', th_cell_center)
        sheet.write(row, col + 12, 'Credit', th_cell_center)
        sheet.write(row, col + 13, 'Balance', th_cell_center)

        # TABLE BODY
        temp_move_id = False
        balance = 0
        is_last_line = False
        narration = ''
        row += 1
        for index, rec in enumerate(accounts_result):
            if rec['move_id'] == 0:
                # opening balance block
                sheet.merge_range(row, col, row, col + 9, rec['entry_label'], td_cell_center_bold)
                sheet.write(row, col + 11, rec['debit'], total_format)
                sheet.write(row, col + 12, rec['credit'], total_format)
                sheet.write(row, col + 13, rec['balance'], total_format)
                row += 1
                balance += rec['balance']
            else:
                if rec['move_id'] != temp_move_id and is_last_line:
                    is_last_line = False
                    sheet.merge_range(row, col, row, col + 13, 'Narration: ' + narration, narration_format)
                    row += 1

                if rec['move_id'] != temp_move_id:
                    temp_move_id = rec['move_id']
                    narration = rec['narration'] if rec['narration'] else ''
                    sheet.write(row, col, ReportUtility.get_date_from_string(rec['date']), td_cell_center_color)
                    sheet.write(row, col + 1, rec['journal_name'], td_cell_center_color)
                    sheet.write(row, col + 2, rec['account_code'], td_cell_left_color)
                    sheet.write(row, col + 3, rec['account_name'], td_cell_left_color)
                    sheet.write(row, col + 4, rec['analytic_account_name'], td_cell_left_color)
                    sheet.write(row, col + 5, rec['operating_unit'], td_cell_center_color)
                    sheet.write(row, col + 6, rec['department_name'], td_cell_left_color)
                    sheet.write(row, col + 7, rec['cost_center'], td_cell_center_color)
                    sheet.write(row, col + 8, rec['reference'], td_cell_left_color)
                    sheet.write(row, col + 9, rec['move_name'], td_cell_center_color)
                    sheet.write(row, col + 10, rec['entry_label'], td_cell_left_color)
                    sheet.write(row, col + 11, rec['debit'], no_format_color)
                    sheet.write(row, col + 12, rec['credit'], no_format_color)

                    if rec['account_code'] == docs.code:

                        balance += rec['balance']
                        sheet.write(row, col + 13, balance, no_format_color)
                    else:
                        sheet.write(row, col + 13, '', no_format_color)
                    row += 1

                    is_last_line = True



                else:
                    sheet.write(row, col, '', td_cell_center)
                    sheet.write(row, col + 1, '', td_cell_center)
                    sheet.write(row, col + 2, rec['account_code'], td_cell_left)
                    sheet.write(row, col + 3, rec['account_name'], td_cell_left)
                    sheet.write(row, col + 4, rec['analytic_account_name'], td_cell_left)
                    sheet.write(row, col + 5, rec['operating_unit'], td_cell_center)
                    sheet.write(row, col + 6, rec['department_name'], td_cell_left)
                    sheet.write(row, col + 7, rec['cost_center'], td_cell_center)
                    sheet.write(row, col + 8, rec['reference'], td_cell_left)
                    sheet.write(row, col + 9, rec['move_name'], td_cell_center)
                    sheet.write(row, col + 10, rec['entry_label'], td_cell_left)
                    sheet.write(row, col + 11, rec['debit'], no_format)
                    sheet.write(row, col + 12, rec['credit'], no_format)

                    if rec['account_code'] == docs.code:
                        balance += rec['balance']
                        sheet.write(row, col + 13, balance, no_format)
                    else:
                        sheet.write(row, col + 13, '', no_format)
                    row += 1

                    is_last_line = True


                if len(accounts_result) - 1 == index:
                    sheet.merge_range(row, col, row, col + 13, 'Narration: ' + narration, narration_format)





AccountGeneralLedgerDetailsXLSX('report.samuda_account_reports.account_general_ledger_details_xlsx', 'account.general.ledger.details.wizard', parser=report_sxw.rml_parse)
