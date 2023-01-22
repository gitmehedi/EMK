from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class TrialBalanceXLSX(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, obj):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = docs['display_account']

        accounts = docs if self.model == 'account.account' else self.env['account.account'].search(
            [('level_id.name', '=', 'Layer 5'), ('tb_filter', '=', docs['is_tb_exc'])])
        used_context = {
            'lang': self.env.context['lang'],
            'operating_unit_ids': docs['operating_unit_ids'].ids,
            'ex_operating_unit_ids': docs['ex_operating_unit_ids'].ids,
            'date_from': docs['date_from'],
            'date_to': docs['date_to'],
            'journal_ids': docs['journal_ids'].ids,
            'state': docs['target_move'],
            'strict_range': True,
            'include_profit_loss': docs['include_profit_loss'],
            'is_tb_exc': docs['is_tb_exc'],
        }
        account_res = self.env['report.account.report_trialbalance'].with_context(used_context)._get_accounts(
            accounts, display_account)

        header_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 12})
        header_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 12})
        format = workbook.add_format({'align': 'left', 'valign': 'top'})
        bold = workbook.add_format({'align': 'left', 'bold': True})
        no_format = workbook.add_format({'num_format': '#,###0.000'})
        total_format = workbook.add_format({'bold': True, 'num_format': '#,###0.000'})

        worksheet = workbook.add_worksheet('Trial Balance')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.merge_range('A1:H2', self.env.user.company_id.name + ': ' + self.title, header_left)

        if docs['display_account']:
            worksheet.write('B5', 'Display Accounts:', bold)
            if docs['display_account'] == 'all':
                display = 'All'
            elif docs['display_account'] == 'movement':
                display = 'With movements'
            else:
                display = 'With balance is not equal to 0'

            worksheet.write('B6', display)

        if docs['date_from']:
            worksheet.write('D5', 'Date From:', bold)
            worksheet.write('E5', docs['date_from'])
        if docs['date_to']:
            worksheet.write('D6', 'Date To:', bold)
            worksheet.write('E6', docs['date_to'])

        if docs['target_move']:
            worksheet.write('F5', 'Target Moves:', bold)
            target = 'All Entries' if docs['target_move'] == 'all' else 'All Posted Entries'
            worksheet.write('F6', target)

        if docs['operating_unit_ids']:
            worksheet.write('F8', 'Branch (Include):', bold)
            worksheet.merge_range('F9:F10', ', '.join([val.name for val in docs['operating_unit_ids']]), format)

        if docs['ex_operating_unit_ids']:
            worksheet.write('G8', 'Branch (Exclude):', bold)
            worksheet.merge_range('G9:G10', ', '.join([val.name for val in docs['ex_operating_unit_ids']]), format)

        row, col = 11, 0

        worksheet.write(row, col, 'Particulars', header_left)
        worksheet.write(row, col + 1, 'Particulars', header_left)
        worksheet.write(row, col + 2, 'GL Head', header_left)
        worksheet.write(row, col + 3, 'CGL Code', header_left)
        worksheet.write(row, col + 4, 'Opening Balance', header_right)
        worksheet.write(row, col + 5, 'Debit', header_right)
        worksheet.write(row, col + 6, 'Credit', header_right)
        worksheet.write(row, col + 7, 'Current Balance', header_right)

        row += 1
        sum = {
            'init_bal': 0,
            'debit': 0,
            'credit': 0,
            'balance': 0,
        }
        for rec in account_res:
            worksheet.write(row, col, rec['sec_layer'])
            worksheet.write(row, col + 1, rec['third_layer'])
            worksheet.write(row, col + 2, rec['name'])
            worksheet.write(row, col + 3, rec['code'])
            worksheet.write(row, col + 4, rec['init_bal'], no_format)
            worksheet.write(row, col + 5, rec['debit'], no_format)
            worksheet.write(row, col + 6, rec['credit'], no_format)
            worksheet.write(row, col + 7, (rec['balance']), no_format)

            sum['init_bal'] += rec['init_bal']
            sum['debit'] += rec['debit']
            sum['credit'] += rec['credit']
            sum['balance'] += rec['balance']
            row += 1

        worksheet.write(row, col + 3, 'Total', total_format)
        worksheet.write(row, col + 4, sum['init_bal'], total_format)
        worksheet.write(row, col + 5, sum['debit'], total_format)
        worksheet.write(row, col + 6, sum['credit'], total_format)
        worksheet.write(row, col + 7, sum['balance'], total_format)


TrialBalanceXLSX('report.account_reports_xls.payroll_xls', 'account.balance.report', parser=report_sxw.rml_parse)
