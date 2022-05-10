from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class AnalyticAccountXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        journal_ids = self.env['account.journal'].search([('type', '!=', 'situation')])

        # Report Utility
        ReportUtility = self.env['report.utility']

        # create context dictionary
        used_context = dict()
        used_context['journal_ids'] = journal_ids.ids or False
        used_context['state'] = 'all' if obj.all_entries else 'posted'
        used_context['date_from'] = obj.date_from
        used_context['date_to'] = obj.date_to
        used_context['analytic_account_ids'] = docs or False
        used_context['strict_range'] = True if obj.date_from else False
        used_context['lang'] = self.env.context.get('lang') or 'en_US'

        # result data
        accounts_result = self.env['accounting.report.utility']._get_account_move_entry(obj, used_context)

        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})

        # table header cell format
        th_cell_left = workbook.add_format(
            {'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_center = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_right = workbook.add_format(
            {'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # table body cell format
        td_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'size': 10, 'border': 1})

        td_cell_center_bold = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # WORKSHEET
        sheet = workbook.add_worksheet('Analytic Report')

        # SET CELL WIDTH
        sheet.set_column(0, 0, 40)
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
        sheet.merge_range(6, 0, 6, 1, "Analytic Account: " + docs.name, bold)
        sheet.merge_range(6, 3, 6, 4, "Date: " + ReportUtility.get_date_from_string(
            obj.date_from) + " To " + ReportUtility.get_date_from_string(obj.date_to), bold)

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


AnalyticAccountXLSX('report.samuda_account_reports.analytic_account_xlsx', 'analytic.account.wizard',
                    parser=report_sxw.rml_parse)
