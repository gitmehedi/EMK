from odoo import fields, models, api, _
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.report import report_sxw


class ExpReferenceXLSX(ReportXlsx):

    @staticmethod
    def get_table_header(sheet, workbook):
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': False, 'size': 8, 'border': 1,
             'text_wrap': True})
        header_format_left.set_font_name('Times New Roman')

        sheet.write(5, 0, "SL", header_format_left)
        sheet.write(5, 1, "Bank Name", header_format_left)
        sheet.write(5, 2, "Exp No", header_format_left)
        sheet.write(5, 3, "HScode", header_format_left)
        sheet.write(5, 4, "Currency", header_format_left)
        sheet.write(5, 5, "Amount Inv", header_format_left)
        sheet.write(5, 6, "Realized Date", header_format_left)
        sheet.write(5, 7, "Amount Realized", header_format_left)
        sheet.write(5, 8, "Ship Date", header_format_left)
        sheet.write(5, 9, "Lc Contact", header_format_left)
        sheet.write(5, 10, "Importer", header_format_left)
        sheet.write(5, 11, "Quantity (MT)", header_format_left)
        sheet.write(5, 12, "Invoice No", header_format_left)
        sheet.write(5, 13, "Invoice Date", header_format_left)
        sheet.write(5, 14, "Incoterm", header_format_left)
        sheet.write(5, 15, "Carrier", header_format_left)
        sheet.write(5, 16, "Dest Port", header_format_left)
        sheet.write(5, 17, "Trans Doc No", header_format_left)
        sheet.write(5, 18, "Trans Doc Date", header_format_left)

    def _get_finalize_table_data(self, sheet, workbook, obj):
        th_cell_center = workbook.add_format(
            {'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 8, 'border': 0})

        query = self._get_sql(obj)
        self.env.cr.execute(query)
        result_data = self.env.cr.dictfetchall()
        row = 6
        for index, rec in enumerate(result_data):
            sheet.write(row, 0, index + 1, th_cell_center)
            sheet.write(row, 1, rec['bank_name'], th_cell_center)
            sheet.write(row, 2, rec['exp_no'], th_cell_center)
            sheet.write(row, 3, rec['hscode'], th_cell_center)
            sheet.write(row, 4, rec['currency'], th_cell_center)
            sheet.write(row, 5, rec['amount_inv'], th_cell_center)
            sheet.write(row, 6, rec['realized_date'], th_cell_center)
            sheet.write(row, 7, rec['amount_realized'], th_cell_center)
            sheet.write(row, 8, rec['ship_date'], th_cell_center)
            sheet.write(row, 9, rec['lc_contact'], th_cell_center)
            sheet.write(row, 10, rec['importer'], th_cell_center)
            sheet.write(row, 11, rec['quantity'], th_cell_center)
            sheet.write(row, 12, rec['invoice_no'], th_cell_center)
            sheet.write(row, 13, rec['invoice_date'], th_cell_center)
            sheet.write(row, 14, rec['incoterm'], th_cell_center)
            sheet.write(row, 15, rec['carrier'], th_cell_center)
            sheet.write(row, 16, rec['dest_port'], th_cell_center)
            sheet.write(row, 17, rec['trans_doc_no'], th_cell_center)
            sheet.write(row, 18, rec['trans_doc_date'], th_cell_center)
            row += 1
            index += 1

    def _get_sql(self, obj):
        where_clauses = self._get_query_where_clause(obj)
        sql_str = """select rb.name as bank_name, ps.exp_number as exp_no, '' as hscode, rc.name as currency, ps.invoice_value as amount_inv,
                    ps.payment_rec_date as realized_date, ps.payment_rec_amount as amount_realized, lc.shipment_date as ship_date,
                    lc.name as lc_contact, rp.name as importer, '0' as quantity, '' as invoice_no, '' as invoice_date,
                    si.name as incoterm, ps.transport_by as carrier, lc.discharge_port as dest_port,
                    '' as trans_doc_no, lc.shipment_date as trans_doc_date
                    from purchase_shipment as ps LEFT JOIN letter_credit as lc ON lc.id=ps.lc_id
                    LEFT JOIN res_partner_bank as rpb on rpb.id = lc.first_party_bank_acc
                    LEFT JOIN res_bank as rb ON rb.id = rpb.bank_id
                    LEFT JOIN res_currency as rc ON rc.id = lc.currency_id
                    LEFT JOIN res_partner as rp ON rp.id = lc.second_party_applicant
                    LEFT JOIN stock_incoterms as si ON si.id = lc.inco_terms
                    """ + where_clauses + """"""
        return sql_str
    def _get_query_where_clause(self, obj):
        if obj.type == 'all':
            type_str = "lc.region_type = 'local' or lc.region_type = 'foreign'"
        else:
            type_str = "lc.region_type=" + obj.type + " "
        return " where ps.payment_rec_date between '" + obj.date_from + "' and '" + obj.date_to + "' and " + type_str

    def generate_xlsx_report(self, workbook, data, obj):
        report_name = "EXP Reference Report"
        sheet = workbook.add_worksheet(report_name)

        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})

        # SET CELL WIDTH
        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 16)
        sheet.set_column(3, 3, 16)
        sheet.set_column(4, 4, 17)
        sheet.set_column(5, 5, 19)
        sheet.set_column(6, 6, 18)
        sheet.set_column(7, 7, 18)

        last_col = 18

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, last_col, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, last_col, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, last_col, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, last_col, self.env.user.company_id.city + '-' + self.env.user.company_id.zip,
                          address_format)
        sheet.merge_range(4, 0, 4, last_col, report_name, name_format)
        self.get_table_header(sheet, workbook)

        self._get_finalize_table_data(sheet, workbook, obj)

        data['name'] = report_name


ExpReferenceXLSX('report.lc_sales_local_report.exp_reference_report',
                 'exp.reference.report', parser=report_sxw.rml_parse)
