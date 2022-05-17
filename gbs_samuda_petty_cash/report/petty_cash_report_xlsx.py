from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class PettyCashReportXLSX(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, obj):
        ReportUtility = self.env['report.utility']
        report_name = 'Petty Cash Report'
        sheet = workbook.add_worksheet(report_name)
        header_bold = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFE0E3', 'bold': True, 'border': 1,
             'size': 10})
        no_format = workbook.add_format({'font_size': 12, 'border': 1, 'num_format': '#,###0.00'})
        normal = workbook.add_format({'font_size': 12, 'border': 1})
        no_format_bold = workbook.add_format({'font_size': 12, 'border': 1, 'bold': True, 'num_format': '#,###0.00'})

        # bg_normal_bordered = workbook.add_format({'font_size': 8, 'bg_color': '#78B0DE', 'border': 1})
        # no_format = workbook.add_format({'num_format': '#,###0.00', 'font_size': 8})
        sheet.merge_range('B2:E2', 'Petty Cash', header_bold)

        row = 3
        col = 1
        sheet.set_column(3, 1, 20)
        sheet.write(row, col, "Reference", normal)
        if obj.name:
            sheet.write(row, col + 1, obj.name, normal)
        else:
            sheet.write(row, col + 1, '', normal)
        sheet.write(row, col + 2, "Starting Balance", normal)
        sheet.write(row, col + 3, obj.balance_start, no_format)
        row = row + 1
        col = 1
        sheet.write(row, col, "Date", normal)
        sheet.write(row, col + 1, ReportUtility.get_date_from_string(obj.date), normal)
        sheet.write(row, col + 2, "Ending Balance", normal)
        sheet.write(row, col + 3, obj.balance_end_real, no_format)
        row = row + 3
        sheet.merge_range('B' + str(row) + ':E' + str(row), 'Transactions', header_bold)

        row = row + 1
        col = 1
        sheet.write(row, col, "Date", normal)
        sheet.write(row, col + 1, "Label", normal)
        sheet.write(row, col + 2, "Reference", normal)
        sheet.write(row, col + 3, "Amount", normal)
        sum_amount = 0.0
        for line in obj.line_ids:
            sum_amount = sum_amount + line.amount
            row = row + 1
            col = 1
            sheet.write(row, col, ReportUtility.get_date_from_string(line.date), normal)
            sheet.write(row, col + 1, line.name, normal)
            if line.ref:
                sheet.write(row, col + 2, line.ref, normal)
            else:
                sheet.write(row, col + 2, '', normal)
            sheet.write(row, col + 3, line.amount, no_format)

        total = sum_amount
        row = row + 1
        col = 3
        sheet.write(row, col, "Total", no_format_bold)
        sheet.write(row, col + 1, float(total), no_format_bold)


PettyCashReportXLSX('report.gbs_samuda_petty_cash.petty_cash_report_xlsx',
                    'account.bank.statement', parser=report_sxw.rml_parse)
