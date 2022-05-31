from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


def date_subtract_date_to_days(date1, date2):
    days = 0
    if date1 and date2:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        days = (d2 - d1).days
    return days




class LcRegisterXLSX(ReportXlsx):

    def get_amount_in_bdt(self, amount, currency):
        if currency == 'BDT':
            return amount
        else:
            res_currency = self.env['res.currency'].search([('name', '=', currency)])
            if res_currency and amount:
                reverse_rate = res_currency.reverse_rate
                return amount * reverse_rate
            else:
                return amount

    def get_delivery_detail(self, lc_id):
        query = """
                select name,min_date,date_done from stock_picking where origin in (select name from sale_order as so LEFT JOIN pi_lc_rel AS plr ON so.pi_id = plr.pi_id where plr.lc_id='%s')
                """ % lc_id
        self.env.cr.execute(query)
        query_res = self.env.cr.dictfetchall()

        lc_delivery_details = []
        lc_delivery_details_str = ''
        for data in query_res:
            lc_delivery_details_str += data['name'] + "," + str(datetime.strptime(data['min_date'], "%Y-%m-%d %H:%M:%S").date()) + "\n"
        date_done = ''
        if query_res:
            date_done = datetime.strptime(query_res[0]['date_done'], "%Y-%m-%d %H:%M:%S").date()
        return lc_delivery_details_str, str(date_done)

    def get_lc_qty_n_delivery_qty(self, lc_id):
        query = """
                select SUM(product_qty) as lc_qty from lc_product_line where lc_id='%s'
                """ % lc_id
        self.env.cr.execute(query)
        query_res = self.env.cr.dictfetchall()
        lc_qty = query_res[0]['lc_qty']
        return lc_qty


    def get_lc_pi_no(self, lc_id):
        query = """
        select name from proforma_invoice as pi LEFT JOIN pi_lc_rel AS plr ON pi.id = plr.pi_id where plr.lc_id='%s'
        """ % lc_id
        self.env.cr.execute(query)
        query_res = self.env.cr.dictfetchall()
        lc_pi_ids = ''
        for data in query_res:
            lc_pi_ids += data['name'] + ", "
        return lc_pi_ids

    def get_lc_so_no(self, lc_id):
        query = """
        select name from sale_order as so LEFT JOIN pi_lc_rel AS plr ON so.pi_id = plr.pi_id where plr.lc_id='%s'
        """ % lc_id
        self.env.cr.execute(query)
        query_res = self.env.cr.dictfetchall()
        lc_so_ids = ''
        for data in query_res:
            lc_so_ids += data['name'] + ", "
        return lc_so_ids

    def generate_xlsx_report(self, workbook, data, obj):

        filter_by = obj.filter_by
        acceptance_default_value = obj.acceptance_default_value
        type = obj.type

        domain = [('lc_id.region_type', '=', type)]
        if type == 'all':
            domain = ['|', ('lc_id.region_type', '=', 'local'), ('lc_id.region_type', '=', 'foreign')]
        docs = self.env['purchase.shipment'].search(domain)
        company_id = docs[0].company_id
        street = docs[0].company_id.street
        street2 = docs[0].company_id.street2
        city_zip_country = docs[0].company_id.city + "-" + docs[0].company_id.zip + ", " + docs[0].company_id.country_id.name
        report_name = "LC Register Report"
        sheet = workbook.add_worksheet(report_name)
        # Then override any that you want.
        sheet.set_default_row(25)
        sheet.set_row(0, 30)
        sheet.set_row(1, 13)
        sheet.set_row(2, 13)
        sheet.set_row(3, 13)
        sheet.set_row(4, 20)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(20, 20, 20)

        # FORMAT
        title_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 22, 'text_wrap': True})
        title_format_center.set_font_name('Times New Roman')

        sub_title_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 10, 'text_wrap': True})
        sub_title_format_center.set_font_name('Times New Roman')

        subject_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 15, 'text_wrap': True})
        subject_format_center.set_font_name('Times New Roman')

        footer_border_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 10})
        footer_border_format_left.set_font_name('Times New Roman')
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 8, 'border': 1,
             'text_wrap': True})
        header_format_left.set_font_name('Times New Roman')
        sub_header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#81d41a', 'bold': False, 'size': 10, 'border': 1,
             'text_wrap': True})
        sub_header_format_left.set_font_name('Times New Roman')
        name_format_left_int = workbook.add_format(
            {'align': 'left', 'border': 1, 'bold': False, 'size': 8, 'text_wrap': True})
        name_border_format_colored = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8, 'text_wrap': True})
        name_border_format_colored.set_font_name('Times New Roman')

        where = ''
        filter_by_text = ''
        if filter_by == 'goods_delivered_doc_not_prepared':
            filter_by_text = 'Goods Delivered but doc. not prepared'
            where += "where ps.doc_preparation_date is null and ps.state = 'receive_doc'"

        elif filter_by == 'first_acceptance':
            filter_by_text = '1st Acceptance'
            # where += "where (ps.to_first_acceptance_date-ps.to_buyer_date) > " + acceptance_default_value + " and ps.to_seller_bank_date is null "
            where += "where (CURRENT_DATE-Date(ps.to_first_acceptance_date)) > " + acceptance_default_value + " and ps.to_seller_bank_date is null "

        elif filter_by == 'second_acceptance':
            filter_by_text = "2nd Acceptance"
            where += "where (CURRENT_DATE-ps.to_seller_bank_date) > " + acceptance_default_value + " and ps.state='to_buyer_bank' "

        elif filter_by == 'maturated_but_amount_not_collect':
            filter_by_text = 'Matured but Amount not collected'
            where += "where payment_rec_date is null and ps.to_seller_bank_date is not null "

        type_text = ''
        if type == 'all':
            type_text = 'Local & Foreign'
            where += " and lc.region_type in ('local', 'foreign')"
        elif type == 'local':
            type_text = 'Local'
            where += "and lc.region_type = 'local'"
        elif type == 'foreign':
            type_text = 'Foreign'
            where += " and lc.region_type = 'foreign'"

        query = '''
                SELECT distinct ps.id, rp.name as party_name,rp2.name as executive_name,lpl.name as product_name, lc.name as lc_number, 
                ps.name as shipment_no, spl.product_qty as shipment_qty, ps.invoice_value as shipment_amount, lc.tenure as tenure,
                ps.bl_date as doc_dispatch_to_party_date_foreign,(ps.to_first_acceptance_date-ps.bl_date) as aging_first_acceptance_days_foreign,
                date(ps.to_first_acceptance_date + INTERVAL '7 day') as to_buyer_bank_date_foreign,
                ps.to_buyer_bank_date as to_buyer_bank_date,ps.to_seller_bank_date as second_acceptance_date,
                (ps.to_buyer_bank_date-ps.to_seller_bank_date) as aging_2nd_acceptance_days, 
                rc.name as currency, 
                lc.id as lc_id, lc.shipment_date as shipment_date, lc.expiry_date as expiry_date, ps.doc_preparation_date as doc_preparation_date,
                lc.issue_date as lc_date,lc.lc_value as lc_amount,lc.region_type as region_type,
                ps.to_buyer_date as doc_dispatch_to_party_date, ps.to_first_acceptance_date as first_acceptance_doc_submission_date,
                (ps.to_first_acceptance_date-ps.to_buyer_date) as aging_first_acceptance_days,ps.to_maturity_date as maturity_date, 
                ps.shipment_done_date as shipment_done_date, 
                ps.discrepancy_amount as discrepancy_amount, ps.ait_amount as ait_amount, ps.payment_rec_date, ps.payment_rec_amount as payment_rec_amount, ps.payment_charge as payment_charge, 
                ps.comment as comment, concat(lc.bank_code, '-', lc.bank_branch) as bank_code, rb.bic as samuda_bank_name,
                pu.name as packing_type, ps.bill_id as bill_id_no
                FROM purchase_shipment AS ps 
                LEFT JOIN letter_credit AS lc ON ps.lc_id = lc.id
                LEFT JOIN res_partner AS rp ON rp.id = lc.second_party_applicant
                LEFT JOIN res_users AS ru ON ru.id = rp.user_id
                LEFT JOIN res_partner AS rp2 ON rp2.id = ru.partner_id
                LEFT JOIN lc_product_line AS lpl ON lpl.lc_id = ps.lc_id
                LEFT JOIN res_currency as rc ON rc.id = lc.currency_id
                LEFT JOIN shipment_product_line AS spl ON ps.id = spl.shipment_id
                LEFT JOIN res_partner_bank AS rpb ON rpb.id = lc.first_party_bank_acc
                LEFT JOIN res_bank AS rb ON rb.id = rpb.bank_id
                LEFT JOIN product_uom AS pu ON pu.id = ps.count_uom ''' + where + '''
                '''
        self.env.cr.execute(query)
        datas_excel = self.env.cr.dictfetchall()
        
        if filter_by == 'goods_delivered_but_lc_not_received':
            filter_by_text = 'Goods Delivered but LC not received'
            datas_excel = []

        # SHEET HEADER
        sheet.merge_range('A1:AP1', company_id.name, title_format_center)
        sheet.merge_range('A2:AP2', street, sub_title_format_center)
        sheet.merge_range('A3:AP3', street2, sub_title_format_center)
        sheet.merge_range('A4:AP4', city_zip_country, sub_title_format_center)
        sheet.merge_range('A5:AP5', "LC Register", subject_format_center)
        sheet.merge_range('A6:AP6', "Filter By: " + filter_by_text + "    Type: " + type_text, header_format_left)

        sheet.write(6, 0, "SL", header_format_left)
        sheet.write(6, 1, "Party Name", header_format_left)
        sheet.write(6, 2, "Executive Name", header_format_left)
        sheet.write(6, 3, "Product Name", header_format_left)
        sheet.write(6, 4, "PI No", header_format_left)
        sheet.write(6, 5, "SO NO", header_format_left)
        sheet.write(6, 6, "LC No", header_format_left)
        sheet.write(6, 7, "LC Date", header_format_left)
        sheet.write(6, 8, "LC Quantity", header_format_left)
        sheet.write(6, 9, "LC Amount", header_format_left)
        sheet.write(6, 10, "Currency", header_format_left)
        sheet.write(6, 11, "LC Delivery Quantity", header_format_left)
        sheet.write(6, 12, "Shipment No", header_format_left)
        sheet.write(6, 13, "Shipment Qty", header_format_left)
        sheet.write(6, 14, "Shipment Amt", header_format_left)
        sheet.write(6, 15, "Shipment Amt in BDT", header_format_left)
        sheet.write(6, 16, "Tenure", header_format_left)
        sheet.write(6, 17, "Shipment Date", header_format_left)
        sheet.write(6, 18, "Expiry date", header_format_left)
        sheet.write(6, 19, "Last Delivery date/Date of Transfer", header_format_left)
        sheet.write(6, 20, "Delivery Details", header_format_left)
        sheet.write(6, 21, "Doc. Preparation Date", header_format_left)
        sheet.write(6, 22, "Aging (Days) Document Prepared", header_format_left)
        sheet.write(6, 23, "Doc. Dispatch to Party Date", header_format_left)
        sheet.write(6, 24, "First Acceptance/ Doc. Submission Date", header_format_left)
        sheet.write(6, 25, "Aging (Days) First Acceptance", header_format_left)
        sheet.write(6, 26, "To Buyer Bank", header_format_left)
        sheet.write(6, 27, "2nd Acceptance Date", header_format_left)
        sheet.write(6, 28, "Aging (Days) 2nd Acceptance", header_format_left)
        sheet.write(6, 29, "Maturity Date", header_format_left)
        sheet.write(6, 30, "Shipment Done Date", header_format_left)
        sheet.write(6, 31, "Discrepancy Amount", header_format_left)
        sheet.write(6, 32, "AIT Amount", header_format_left)
        sheet.write(6, 33, "Payment Rec. Date", header_format_left)
        sheet.write(6, 34, "Payment Rece. Amount", header_format_left)
        sheet.write(6, 35, "Payment Charge", header_format_left)
        sheet.write(6, 36, "Discrepancy Details", header_format_left)
        sheet.write(6, 37, "Aging /(Days) Final Payment", header_format_left)
        sheet.write(6, 38, "Party Bank & Branch", header_format_left)
        sheet.write(6, 39, "Samuda Bank Name", header_format_left)
        sheet.write(6, 40, "Packing Type", header_format_left)
        sheet.write(6, 41, "Bill ID NO", header_format_left)

        data['name'] = report_name

        sl = 0
        row = 6
        for data in datas_excel:
            sl = sl + 1
            row = row + 1
            delivery_details_date_of_trans = self.get_delivery_detail(data['lc_id'])
            region_type = data['region_type']

            sheet.write(row, 0, sl, name_format_left_int)
            sheet.write(row, 1, data['party_name'], name_border_format_colored)
            sheet.write(row, 2, data['executive_name'], name_border_format_colored)
            sheet.write(row, 3, data['product_name'], name_border_format_colored)
            sheet.write(row, 4, self.get_lc_pi_no(data['lc_id']), name_border_format_colored)
            sheet.write(row, 5, self.get_lc_so_no(data['lc_id']), name_border_format_colored)
            sheet.write(row, 6, data['lc_number'], name_border_format_colored)
            sheet.write(row, 7, data['lc_date'], name_border_format_colored)
            sheet.write(row, 8, self.get_lc_qty_n_delivery_qty(data['lc_id']), name_border_format_colored)
            sheet.write(row, 9, data['lc_amount'], name_border_format_colored)
            sheet.write(row, 10, data['currency'], name_border_format_colored)
            sheet.write(row, 11, '', name_border_format_colored)
            sheet.write(row, 12, data['shipment_no'], name_border_format_colored)
            sheet.write(row, 13, data['shipment_qty'], name_border_format_colored)
            sheet.write(row, 14, data['shipment_amount'], name_border_format_colored)
            sheet.write(row, 15, self.get_amount_in_bdt(data['shipment_amount'], data['currency']), name_border_format_colored)
            sheet.write(row, 16, data['tenure'], name_border_format_colored)
            sheet.write(row, 17, data['shipment_date'], name_border_format_colored)
            sheet.write(row, 18, data['expiry_date'], name_border_format_colored)
            sheet.write(row, 19, delivery_details_date_of_trans[1], name_border_format_colored)
            sheet.write(row, 20, delivery_details_date_of_trans[0], name_border_format_colored)
            sheet.write(row, 21, data['doc_preparation_date'], name_border_format_colored)
            sheet.write(row, 22, date_subtract_date_to_days(data['doc_preparation_date'], delivery_details_date_of_trans[1]), name_border_format_colored)

            if region_type == 'local':
                sheet.write(row, 23, data['doc_dispatch_to_party_date'], name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 23, data['doc_dispatch_to_party_date_foreign'], name_border_format_colored)

            sheet.write(row, 24, data['first_acceptance_doc_submission_date'], name_border_format_colored)

            if region_type == 'local':
                sheet.write(row, 25, data['aging_first_acceptance_days'], name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 25, data['aging_first_acceptance_days_foreign'], name_border_format_colored)
            else:
                a = '10'
            if region_type == 'local':
                sheet.write(row, 26, data['to_buyer_bank_date'], name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 26, data['to_buyer_bank_date_foreign'], name_border_format_colored)
            if region_type == 'local':
                sheet.write(row, 27, data['second_acceptance_date'], name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 27, 'N/A', name_border_format_colored)
            if region_type == 'local':
                sheet.write(row, 28, data['aging_2nd_acceptance_days'], name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 28, 'N/A', name_border_format_colored)

            sheet.write(row, 29, data['maturity_date'], name_border_format_colored)
            sheet.write(row, 30, data['shipment_done_date'], name_border_format_colored)
            sheet.write(row, 31, data['discrepancy_amount'], name_border_format_colored)

            if region_type == 'local':
                sheet.write(row, 32, data['ait_amount'], name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 32, 'N/A', name_border_format_colored)

            sheet.write(row, 33, data['payment_rec_date'], name_border_format_colored)
            sheet.write(row, 34, data['payment_rec_amount'], name_border_format_colored)
            sheet.write(row, 35, data['payment_charge'], name_border_format_colored)
            sheet.write(row, 36, data['comment'], name_border_format_colored)
            sheet.write(row, 37, date_subtract_date_to_days(data['shipment_done_date'], data['maturity_date']), name_border_format_colored)
            sheet.write(row, 38, data['bank_code'], name_border_format_colored)
            sheet.write(row, 39, data['samuda_bank_name'], name_border_format_colored)
            sheet.write(row, 40, data['packing_type'], name_border_format_colored)
            sheet.write(row, 41, data['bill_id_no'], name_border_format_colored)


LcRegisterXLSX('report.lc_sales_local_report.lc_register_report',
                   'lc.register.wizard', parser=report_sxw.rml_parse)
