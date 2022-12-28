from odoo import fields, models, api, _
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.report import report_sxw


class ExpReferenceXLSX(ReportXlsx):

    @staticmethod
    def get_table_header(sheet, workbook):
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 8, 'border': 1,
             'text_wrap': True})
        header_format_left.set_font_name('Times New Roman')
        row = 7
        sheet.write(row, 0, "SL", header_format_left)
        sheet.write(row, 1, "Bank Name", header_format_left)
        sheet.write(row, 2, "Exp No", header_format_left)
        sheet.write(row, 3, "HScode", header_format_left)
        sheet.write(row, 4, "Currency", header_format_left)
        sheet.write(row, 5, "Amount Inv", header_format_left)
        sheet.write(row, 6, "Realized Date", header_format_left)
        sheet.write(row, 7, "Amount Realized", header_format_left)
        sheet.write(row, 8, "Ship Date", header_format_left)
        sheet.write(row, 9, "Lc Contact", header_format_left)
        sheet.write(row, 10, "Importer", header_format_left)
        sheet.write(row, 11, "Quantity (MT)", header_format_left)
        sheet.write(row, 12, "Invoice No", header_format_left)
        sheet.write(row, 13, "Invoice Date", header_format_left)
        sheet.write(row, 14, "Incoterm", header_format_left)
        sheet.write(row, 15, "Carrier", header_format_left)
        sheet.write(row, 16, "Dest Port", header_format_left)
        sheet.write(row, 17, "Trans Doc No", header_format_left)
        sheet.write(row, 18, "Trans Doc Date", header_format_left)

    def _get_finalize_table_data(self, sheet, workbook, obj):
        th_cell_center = workbook.add_format(
            {'align': 'left', 'valign': 'vcenter', 'bold': False, 'size': 8, 'border': 1})
        th_cell_signature = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': False, 'size': 8, 'border': 0})

        th_cell_numeric = workbook.add_format(
            {'align': 'right', 'valign': 'vcenter', 'bold': False, 'size': 8, 'border': 1})
        query = self._get_sql(obj)
        self.env.cr.execute(query)
        result_data = self.env.cr.dictfetchall()
        row = 8
        for index, rec in enumerate(result_data):
            sheet.write(row, 0, index + 1, th_cell_center)
            sheet.write(row, 1, rec['bank_name'], th_cell_center)
            sheet.write(row, 2, rec['exp_no'], th_cell_center)
            sheet.write(row, 3, rec['hscode'], th_cell_center)
            sheet.write(row, 4, rec['currency'], th_cell_center)
            sheet.write(row, 5, "{:.2f}".format(rec['amount_inv']), th_cell_numeric)
            sheet.write(row, 6, rec['realized_date'], th_cell_center)
            a = rec['amount_realized']
            sheet.write(row, 7, "{:.2f}".format(rec['amount_realized']), th_cell_numeric)
            sheet.write(row, 8, rec['ship_date'], th_cell_center)
            sheet.write(row, 9, rec['lc_contact'], th_cell_center)
            sheet.write(row, 10, rec['importer'], th_cell_center)
            sheet.write(row, 11, rec['quantity'], th_cell_numeric)
            sheet.write(row, 12, rec['invoice_no'], th_cell_center)
            sheet.write(row, 13, rec['invoice_date'], th_cell_center)
            sheet.write(row, 14, rec['incoterm'], th_cell_center)
            sheet.write(row, 15, rec['carrier'], th_cell_center)
            sheet.write(row, 16, rec['dest_port'], th_cell_center)
            sheet.write(row, 17, rec['trans_doc_no'], th_cell_center)
            sheet.write(row, 18, rec['trans_doc_date'], th_cell_center)
            row += 1
            index += 1

        # Signature
        row += 3
        sheet.write(row, 1, "Signature", th_cell_signature)
        sheet.write(row, 17, "Signature", th_cell_signature)
    def _get_sql(self, obj):
        where_clauses = self._get_query_where_clause(obj)
        if obj.type == 'local':
            sql_str = """select string_agg(hs_code.display_name, ',') as hscode, bank_name, exp_no, currency,amount_inv,realized_date,amount_realized,ship_date,lc_contact,importer,quantity,invoice_no,invoice_date,incoterm,carrier,dest_port,trans_doc_no,trans_doc_date  from (
                            select split_part(ip.value_reference::TEXT, ',', 2)::INTEGER as hs_code_id,rb.name as bank_name, ps.exp_number as exp_no, rc.name as currency, COALESCE(ps.invoice_value,0) as amount_inv,
                            ps.payment_rec_date as realized_date, COALESCE(ps.payment_rec_amount,0) as amount_realized, lc.shipment_date as ship_date,
                            lc.name as lc_contact, rp.name as importer, SUM(spl.product_qty) as quantity, string_agg(ai.move_name, ', ') as invoice_no, MAX(ai.date_invoice) as invoice_date,
                            si.name as incoterm, ps.transport_by as carrier, lc.discharge_port as dest_port,
                            '' as trans_doc_no, lc.shipment_date as trans_doc_date
                            from purchase_shipment as ps LEFT JOIN letter_credit as lc ON lc.id=ps.lc_id
                            LEFT JOIN res_partner_bank as rpb on rpb.id = lc.first_party_bank_acc
                            LEFT JOIN res_bank as rb ON rb.id = rpb.bank_id
                            LEFT JOIN res_currency as rc ON rc.id = lc.currency_id
                            LEFT JOIN res_partner as rp ON rp.id = lc.second_party_applicant
                            LEFT JOIN stock_incoterms as si ON si.id = lc.inco_terms
                            LEFT JOIN lc_product_line as lpl ON lpl.lc_id = lc.id
                            LEFT JOIN product_product as pp ON pp.id = lpl.product_id
                            LEFT JOIN product_template as pt ON pt.id = pp.product_tmpl_id
                            LEFT JOIN shipment_product_line as spl ON spl.shipment_id = ps.id
                            LEFT JOIN lc_shipment_invoice_rel as lsir ON lsir.shipment_id = ps.id
                            LEFT JOIN account_invoice as ai ON ai.id = lsir.invoice_id 
                            LEFT JOIN ir_property as ip ON (ip.res_id = concat('product.template,', pt.id::text) and ip.name = 'hs_code_id')
                            """ + where_clauses + """
                            group by ps.name, ip.value_reference,rb.name, ps.exp_number, rc.name, ps.invoice_value, ps.payment_rec_date, ps.payment_rec_amount,
                            lc.shipment_date, lc.name, rp.name, si.name, ps.transport_by, lc.discharge_port, lc.shipment_date
                    ) as sub LEFT JOIN hs_code ON sub.hs_code_id = hs_code.id 
                    group by bank_name,exp_no,currency,amount_inv,realized_date,amount_realized,ship_date,lc_contact,
                    importer,quantity,invoice_no,invoice_date,incoterm,carrier,dest_port,trans_doc_no,trans_doc_date
                        """
        elif obj.type == 'foreign':
            sql_str = """
            select string_agg(hs_code.display_name, ',') as hscode, bank_name, exp_no, currency,amount_inv,realized_date,amount_realized,ship_date,lc_contact,importer,quantity,invoice_no,invoice_date,incoterm,carrier,dest_port,trans_doc_no,trans_doc_date  from (
                    select split_part(ip.value_reference::TEXT, ',', 2)::INTEGER as hs_code_id,rb.name as bank_name, ps.exp_number as exp_no, '' as hscode, rc.name as currency, ps.invoice_value as amount_inv,
                    ps.payment_rec_date as realized_date, COALESCE(ps.payment_rec_amount,0) as amount_realized, lc.shipment_date as ship_date,
                    lc.name as lc_contact, rp.name as importer, SUM(lpl.product_qty) as quantity, ps.invoice_number_dummy as invoice_no, ps.invoice_date_dummy as invoice_date,
                    si.name as incoterm, ps.transport_by as carrier, lc.discharge_port as dest_port,
                    ps.truck_receipt_no as trans_doc_no, ps.bl_date as trans_doc_date
                    from purchase_shipment as ps LEFT JOIN letter_credit as lc ON lc.id=ps.lc_id
                    LEFT JOIN res_partner_bank as rpb on rpb.id = lc.first_party_bank_acc
                    LEFT JOIN res_bank as rb ON rb.id = rpb.bank_id
                    LEFT JOIN res_currency as rc ON rc.id = lc.currency_id
                    LEFT JOIN res_partner as rp ON rp.id = lc.second_party_applicant
                    LEFT JOIN stock_incoterms as si ON si.id = lc.inco_terms
                    LEFT JOIN lc_product_line as lpl ON lpl.lc_id = lc.id
                    LEFT JOIN product_product as pp ON pp.id = lpl.product_id
                    LEFT JOIN product_template as pt ON pt.id = pp.product_tmpl_id
                    LEFT JOIN shipment_product_line as spl ON spl.shipment_id = ps.id
                    LEFT JOIN lc_shipment_invoice_rel as lsir ON lsir.shipment_id = ps.id
                    LEFT JOIN ir_property as ip ON (ip.res_id = concat('product.template,', pt.id::text) and ip.name = 'hs_code_id')
                    where lc.name='SC-SCCL-CTG-2022-004221'
                    group by ps.name, rb.name, ps.exp_number, rc.name, ps.invoice_value, ps.payment_rec_date, ps.payment_rec_amount,
                    lc.shipment_date, lc.name, rp.name, si.name, ps.transport_by, lc.discharge_port, ps.bl_date, ps.invoice_number_dummy, ps.invoice_date_dummy,ps.truck_receipt_no,ip.value_reference
            ) as sub LEFT JOIN hs_code ON sub.hs_code_id = hs_code.id 
            group by bank_name,exp_no,currency,amount_inv,realized_date,amount_realized,ship_date,lc_contact,
            importer,quantity,invoice_no,invoice_date,incoterm,carrier,dest_port,trans_doc_no,trans_doc_date
            """

        return sql_str
    def _get_query_where_clause(self, obj):
        if obj.type == 'all':
            type_str = "lc.region_type = 'local' or lc.region_type = 'foreign'"
        else:
            type_str = "lc.region_type='" + obj.type + "' "
        return " where ps.payment_rec_date between '" + obj.date_from + "' and '" + obj.date_to + "' and " + type_str

    def generate_xlsx_report(self, workbook, data, obj):
        report_name = "EXP Reference Report"
        sheet = workbook.add_worksheet(report_name)
        ReportUtility = self.env['report.utility']

        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})
        left_text_format = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10})

        # SET CELL WIDTH
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 25)
        sheet.set_column(11, 11, 15)
        sheet.set_column(12, 12, 15)
        sheet.set_column(13, 13, 15)
        sheet.set_column(14, 14, 15)
        sheet.set_column(15, 15, 15)
        sheet.set_column(16, 16, 15)
        sheet.set_column(17, 17, 15)
        sheet.set_column(18, 18, 15)

        last_col = 18

        filter_by_date = "Date: " + ReportUtility.get_date_from_string(
            obj.date_from) + " To " + ReportUtility.get_date_from_string(obj.date_to)
        condition_str = "Local" if obj.type == 'local' else "Foreign"
        filter_by_type = "Type: " + condition_str

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, last_col, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, last_col, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, last_col, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, last_col, self.env.user.company_id.city + '-' + self.env.user.company_id.zip,
                          address_format)
        sheet.merge_range(4, 0, 4, last_col, report_name, name_format)
        sheet.merge_range(5, 0, 5, last_col, filter_by_date, left_text_format)
        sheet.merge_range(6, 0, 6, last_col, filter_by_type, left_text_format)
        self.get_table_header(sheet, workbook)

        self._get_finalize_table_data(sheet, workbook, obj)

        data['name'] = report_name


ExpReferenceXLSX('report.lc_sales_local_report.exp_reference_report',
                 'exp.reference.report', parser=report_sxw.rml_parse)
