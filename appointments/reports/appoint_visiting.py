from odoo import models, fields


class VisitingCardXlsx(models.AbstractModel):
    _name = 'report.appointments.report_appoint_visiting_xls'
    # _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter', })
        sheet = workbook.add_worksheet('Patient Card')
        sheet.write(2, 2, 'Name', format1)
        sheet.write(2, 3, lines.first_name, format2)
        sheet.write(3, 2, 'Age', format1)
        sheet.write(3, 3, lines.last_name, format2)