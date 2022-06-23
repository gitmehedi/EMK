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


def get_sheet_table_head(sheet, workbook):
    header_format_left = workbook.add_format(
        {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 8, 'border': 1,
         'text_wrap': True})
    header_format_left.set_font_name('Times New Roman')

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
    sheet.write(6, 16, "Undelivered Quantity", header_format_left)
    sheet.write(6, 17, "Tenure", header_format_left)
    sheet.write(6, 18, "Shipment Date", header_format_left)
    sheet.write(6, 19, "Expiry date", header_format_left)
    sheet.write(6, 20, "Last Delivery date/Date of Transfer", header_format_left)
    sheet.write(6, 21, "Delivery Details", header_format_left)
    sheet.write(6, 22, "Doc. Preparation Date", header_format_left)
    sheet.write(6, 23, "Aging (Days) Document Prepared", header_format_left)
    sheet.write(6, 24, "Doc. submit to Party Date/1st Acceptance", header_format_left)
    sheet.write(6, 25, "First Acceptance Doc. Collection  Date", header_format_left)
    sheet.write(6, 26, "Aging (Days) First Acceptance", header_format_left)
    sheet.write(6, 27, "To Buyer Bank", header_format_left)
    sheet.write(6, 28, "2nd Acceptance Date", header_format_left)
    sheet.write(6, 29, "Aging (Days) 2nd Acceptance", header_format_left)
    sheet.write(6, 30, "Maturity Date", header_format_left)
    sheet.write(6, 31, "Shipment Done Date", header_format_left)
    sheet.write(6, 32, "Discrepancy Amount", header_format_left)
    sheet.write(6, 33, "AIT Amount", header_format_left)
    sheet.write(6, 34, "Payment Rec. Date", header_format_left)
    sheet.write(6, 35, "Payment Rece. Amount", header_format_left)
    sheet.write(6, 36, "Payment Charge", header_format_left)
    sheet.write(6, 37, "Discrepancy Details", header_format_left)
    sheet.write(6, 38, "Aging /(Days) Final Payment", header_format_left)
    sheet.write(6, 39, "Party Bank & Branch", header_format_left)
    sheet.write(6, 40, "Samuda Bank Name", header_format_left)
    sheet.write(6, 41, "Packing Type", header_format_left)
    sheet.write(6, 42, "Bill ID NO", header_format_left)


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
        if not lc_id:
            return 0, 0
        query = """
                select name,min_date,date_done from stock_picking where origin in (select name from sale_order as so LEFT JOIN pi_lc_rel AS plr ON so.pi_id = plr.pi_id where plr.lc_id='%s')
                """ % lc_id
        self.env.cr.execute(query)
        query_res = self.env.cr.dictfetchall()

        lc_delivery_details = []
        lc_delivery_details_str = ''
        for data in query_res:
            lc_delivery_details_str += data['name'] + "," + str(
                datetime.strptime(data['min_date'], "%Y-%m-%d %H:%M:%S").date()) + "\n"
        date_done = ''
        if query_res:
            date_done = datetime.strptime(query_res[0]['date_done'], "%Y-%m-%d %H:%M:%S").date()
        return lc_delivery_details_str, str(date_done)

    def get_lc_qty_n_delivery_qty(self, lc_id):
        if not lc_id:
            return '',''
        query = """
                select SUM(product_qty) as lc_qty from lc_product_line where lc_id='%s'
                """ % lc_id
        self.env.cr.execute(query)
        query_res = self.env.cr.dictfetchall()
        lc_qty = query_res[0]['lc_qty']
        delivered_qty = ''
        return lc_qty, delivered_qty

    def get_lc_pi_no(self, lc_id):
        if not lc_id:
            return ''

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
        if not lc_id:
            return ''

        query = """
        select name from sale_order as so LEFT JOIN pi_lc_rel AS plr ON so.pi_id = plr.pi_id where plr.lc_id='%s'
        """ % lc_id
        self.env.cr.execute(query)
        query_res = self.env.cr.dictfetchall()
        lc_so_ids = ''
        for data in query_res:
            lc_so_ids += data['name'] + ", "
        return lc_so_ids

    def get_sheet_header(self, sheet, docs, workbook, filter_by_text, type_text):
        title_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 22, 'text_wrap': True})
        title_format_center.set_font_name('Times New Roman')
        sub_title_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 10, 'text_wrap': True})
        sub_title_format_center.set_font_name('Times New Roman')
        subject_format_center = workbook.add_format({'align': 'center', 'bold': False, 'size': 15, 'text_wrap': True})
        subject_format_center.set_font_name('Times New Roman')
        header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 8, 'border': 1,
             'text_wrap': True})
        header_format_left.set_font_name('Times New Roman')

        company_id = docs[0].company_id
        street = docs[0].company_id.street
        street2 = docs[0].company_id.street2
        city_zip_country = docs[0].company_id.city + "-" + docs[0].company_id.zip + ", " + docs[
            0].company_id.country_id.name

        sheet.merge_range('A1:AP1', company_id.name, title_format_center)
        sheet.merge_range('A2:AP2', street, sub_title_format_center)
        sheet.merge_range('A3:AP3', street2, sub_title_format_center)
        sheet.merge_range('A4:AP4', city_zip_country, sub_title_format_center)
        sheet.merge_range('A5:AP5', "LC Register", subject_format_center)
        sheet.merge_range('A6:AP6', "Filter By: " + filter_by_text + "    Type: " + type_text, header_format_left)

    def set_sheet_table_data(self, sheet, workbook, datas):
        name_format_left_int = workbook.add_format(
            {'align': 'left', 'border': 1, 'bold': False, 'size': 8, 'text_wrap': True})
        name_border_format_colored = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'border': 1, 'valign': 'vcenter', 'bold': False, 'size': 8,
             'text_wrap': True})
        name_border_format_colored.set_font_name('Times New Roman')

        sl = 0
        row = 6
        for data in datas:
            sl = sl + 1
            row = row + 1
            lc_id = data['lc_id'] if 'lc_id' in data else ''
            delivery_details_date_of_trans = self.get_delivery_detail(lc_id)
            lc_and_delivered_qty = self.get_lc_qty_n_delivery_qty(lc_id)
            region_type = data['region_type'] if 'region_type' in data else ''

            sheet.write(row, 0, sl, name_format_left_int)
            sheet.write(row, 1, data['party_name'], name_border_format_colored)
            sheet.write(row, 2, data['executive_name'], name_border_format_colored)
            sheet.write(row, 3, data['product_name'], name_border_format_colored)
            sheet.write(row, 4, self.get_lc_pi_no(lc_id) if lc_id != '' else data['pi_name'], name_border_format_colored)
            sheet.write(row, 5, self.get_lc_so_no(lc_id) if lc_id != '' else data['so_name'], name_border_format_colored)
            sheet.write(row, 6, data['lc_number'] if 'lc_number' in data else '', name_border_format_colored)
            sheet.write(row, 7, data['lc_date'] if 'lc_date' in data else '', name_border_format_colored)
            sheet.write(row, 8, lc_and_delivered_qty[0], name_border_format_colored)
            sheet.write(row, 9, data['lc_amount'] if 'lc_amount' in data else '', name_border_format_colored)
            sheet.write(row, 10, data['currency'] if 'currency' in data else '', name_border_format_colored)
            sheet.write(row, 11, lc_and_delivered_qty[1] if lc_id != '' else data['qty_delivery'], name_border_format_colored)
            sheet.write(row, 12, data['shipment_no'] if 'shipment_no' in data else '', name_border_format_colored)
            sheet.write(row, 13, data['shipment_qty'] if 'shipment_qty' in data else '', name_border_format_colored)
            sheet.write(row, 14, data['shipment_amount'] if 'shipment_amount' in data else '', name_border_format_colored)
            sheet.write(row, 15, self.get_amount_in_bdt(data['shipment_amount'] if 'shipment_amount' in data else '', data['currency'] if 'currency' in data else ''),
                        name_border_format_colored)
            sheet.write(row, 16, '0', name_border_format_colored)
            sheet.write(row, 17, data['tenure'] if 'tenure' in data else '', name_border_format_colored)
            sheet.write(row, 18, data['shipment_date'] if 'shipment_date' in data else '', name_border_format_colored)
            sheet.write(row, 19, data['expiry_date'] if 'expiry_date' in data else '', name_border_format_colored)
            sheet.write(row, 20, delivery_details_date_of_trans[1], name_border_format_colored)
            sheet.write(row, 21, delivery_details_date_of_trans[0], name_border_format_colored)
            sheet.write(row, 22, data['doc_preparation_date'] if 'doc_preparation_date' in data else '', name_border_format_colored)
            sheet.write(row, 23, date_subtract_date_to_days(data['doc_preparation_date'] if 'doc_preparation_date' in data else '', delivery_details_date_of_trans[1]),
                        name_border_format_colored)

            if region_type == 'local':
                sheet.write(row, 24, data['doc_dispatch_to_party_date'] if 'doc_dispatch_to_party_date' in data else '', name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 24, data['doc_dispatch_to_party_date_foreign'] if 'doc_dispatch_to_party_date_foreign' in data else '', name_border_format_colored)

            sheet.write(row, 25, data['first_acceptance_doc_submission_date'] if 'first_acceptance_doc_submission_date' in data else '', name_border_format_colored)

            if region_type == 'local':
                sheet.write(row, 26, data['aging_first_acceptance_days'] if 'aging_first_acceptance_days' in data else '', name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 26, data['aging_first_acceptance_days_foreign'] if 'aging_first_acceptance_days_foreign' in data else '', name_border_format_colored)

            if region_type == 'local':
                sheet.write(row, 27, data['to_buyer_bank_date'] if 'to_buyer_bank_date' in data else '', name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 27, data['to_buyer_bank_date_foreign'] if 'to_buyer_bank_date_foreign' in data else '', name_border_format_colored)
            if region_type == 'local':
                sheet.write(row, 28, data['second_acceptance_date'] if 'second_acceptance_date' in data else '', name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 28, 'N/A', name_border_format_colored)
            if region_type == 'local':
                sheet.write(row, 29, data['aging_2nd_acceptance_days'] if 'aging_2nd_acceptance_days' in data else '', name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 29, 'N/A', name_border_format_colored)

            sheet.write(row, 30, data['maturity_date'] if 'maturity_date' in data else '', name_border_format_colored)
            sheet.write(row, 31, data['shipment_done_date'] if 'shipment_done_date' in data else '', name_border_format_colored)
            sheet.write(row, 32, data['discrepancy_amount'] if 'discrepancy_amount' in data else '', name_border_format_colored)

            if region_type == 'local':
                sheet.write(row, 33, data['ait_amount'] if 'ait_amount' in data else '', name_border_format_colored)
            elif region_type == 'foreign':
                sheet.write(row, 33, 'N/A', name_border_format_colored)

            sheet.write(row, 34, data['payment_rec_date'] if 'payment_rec_date' in data else '', name_border_format_colored)
            sheet.write(row, 35, data['payment_rec_amount'] if 'payment_rec_amount' in data else '', name_border_format_colored)
            sheet.write(row, 36, data['payment_charge'] if 'payment_charge' in data else '', name_border_format_colored)
            sheet.write(row, 37, data['comment'] if 'comment' in data else '', name_border_format_colored)
            sheet.write(row, 38, date_subtract_date_to_days(data['shipment_done_date'] if 'shipment_done_date' in data else '', data['maturity_date'] if 'maturity_date' in data else ''),
                        name_border_format_colored)
            sheet.write(row, 39, data['bank_code'] if 'bank_code' in data else '', name_border_format_colored)
            sheet.write(row, 40, data['samuda_bank_name'] if 'samuda_bank_name' in data else '', name_border_format_colored)
            sheet.write(row, 41, data['packing_type'] if 'packing_type' in data else '', name_border_format_colored)
            sheet.write(row, 42, data['bill_id_no'] if 'bill_id_no' in data else '', name_border_format_colored)

    def generate_xlsx_report(self, workbook, data, obj):

        filter_by = obj.filter_by
        acceptance_default_value = obj.acceptance_default_value
        type = obj.type

        domain = [('lc_id.region_type', '=', type)]
        if type == 'all':
            domain = ['|', ('lc_id.region_type', '=', 'local'), ('lc_id.region_type', '=', 'foreign')]
        docs = self.env['purchase.shipment'].search(domain)

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

        footer_border_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bold': True, 'size': 10})
        footer_border_format_left.set_font_name('Times New Roman')

        sub_header_format_left = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'left', 'bg_color': '#81d41a', 'bold': False, 'size': 10, 'border': 1,
             'text_wrap': True})
        sub_header_format_left.set_font_name('Times New Roman')

        where = ''
        filter_by_text = ''
        if filter_by == 'goods_delivered_doc_not_prepared':
            filter_by_text = 'Goods Delivered but doc. not prepared'
            where += "where ps.doc_preparation_date is null and ps.state = 'receive_doc'"

        elif filter_by == 'first_acceptance':
            filter_by_text = '1st Acceptance'
            where += "where (CURRENT_DATE-Date(ps.to_first_acceptance_date)) > " + acceptance_default_value + " and ps.to_seller_bank_date is null "

        elif filter_by == 'second_acceptance':
            filter_by_text = "2nd Acceptance"
            where += "where (CURRENT_DATE-ps.to_seller_bank_date) > " + acceptance_default_value + " and ps.state='to_buyer_bank' "

        elif filter_by == 'maturated_but_amount_not_collect':
            filter_by_text = 'Matured but Amount not collected'
            where += "where payment_rec_date is null and ps.to_seller_bank_date is not null "
        elif filter_by == 'percentage_of_first_acceptance_collection':
            filter_by_text = 'Percentage of First Acceptance Collection'
            where += "where ps.create_date >= '" + obj.date_from + "' and ps.create_date <= '" + obj.date_to + "' "
        elif filter_by == 'lc_history':
            filter_by_text = 'LC History'
            where = ''
        elif filter_by == 'lc_number':
            filter_by_text = 'LC Number: ' + obj.lc_number.name
            where += "where lc.id ='" + str(obj.lc_number.id) + "'"

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

            query = '''
                select rp.name as party_name, rp2.name as executive_name,sol.name as product_name, so.region_type as region_type, so.name as so_name, 
                pi.name as pi_name,rc.name as currency, sol.qty_delivered as qty_delivery
                from sale_order as so 
                LEFT JOIN sale_order_type as sot on so.type_id = sot.id 
                LEFT JOIN sale_order_line as sol on so.id = sol.order_id
                LEFT JOIN res_partner as rp on so.partner_id = rp.id
                LEFT JOIN res_partner as rp2 on so.user_id = rp2.id
                LEFT JOIN proforma_invoice as pi on pi.id = so.pi_id
                LEFT JOIN product_pricelist as ppl on ppl.id = so.pricelist_id
                LEFT JOIN res_currency as rc on rc.id = ppl.currency_id
                where so.lc_id is null
                and sot.sale_order_type='lc_sales' and sol.qty_delivered > 0
            '''
            self.env.cr.execute(query)
            datas_excel = self.env.cr.dictfetchall()
            #datas_excel = []

        # SHEET HEADER
        self.get_sheet_header(sheet, docs, workbook, filter_by_text, type_text)

        get_sheet_table_head(sheet, workbook)

        self.set_sheet_table_data(sheet, workbook, datas_excel)

        data['name'] = report_name


LcRegisterXLSX('report.lc_sales_local_report.lc_register_report',
               'lc.register.wizard', parser=report_sxw.rml_parse)
