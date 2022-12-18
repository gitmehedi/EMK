import datetime
from datetime import datetime, timedelta
from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class LandedCostInfoXLSX(ReportXlsx):

    def get_main_table_data(self, landed_cost_id, product_id):
        main_table_data_list = []

        main_tbl_query = """
            select *, 
                100*(total_expense_amount_per_account/(total_cost_without_landed_cost + 
                (SUM(total_expense_amount_per_account) OVER()))) as amt_percentage
                from (
                        select 
                            account_id,
                            acc_name,
                            product_qty,
                            sum(expense_amount) as total_expense_amount_per_account,
                            (sum(expense_amount)/sub.product_qty) as total_cost_ratio_per_account,
                             sub.product_qty*sub.standard_price_old as total_cost_without_landed_cost
                            from 
                            (select 
                            *,concat(aa.code,' ',aa.name) as acc_name
                            from 
                            purchase_cost_distribution_line_expense as line_child 
                            left join purchase_cost_distribution_line as line on line.id = line_child.distribution_line
                            left join purchase_cost_distribution as main on main.id = line.distribution
                            left join account_account as aa on aa.id = line_child.account_id
                            left join ir_property ON (ir_property.value_reference = concat('account.account,', aa.id::text) AND ir_property.name = 'property_account_expense_id')
                            left join product_template as pt ON (ir_property.res_id = concat('product.template,', pt.id::text)) 
        
                            left join product_product as pp on pp.product_tmpl_id = pt.id
                            where main.id = %s
                            and line.product_id = %s
                            and(pt.is_duty_tax = False or pt.is_duty_tax is null)) sub
                            group by sub.account_id,product_qty,sub.standard_price_old,sub.acc_name
                ) sub_2 
                """ % (landed_cost_id, product_id)

        self.env.cr.execute(main_tbl_query)
        for row in self.env.cr.dictfetchall():
            main_table_data_list.append(row)
        return main_table_data_list

    def get_history_table_data(self, landed_cost_id, product_id):
        history_table_data_list = []
        cost_history_tbl_query = """

                        SELECT 
                                id as main_id,
                                DATE(datetime) as cost_update, 
                                name as lc_number,
                                sum(product_qty) as product_qty,
                                cost as unit_cost
                                FROM 
                                (
                                    SELECT 
                                    main.id,
                                    pph.datetime,
                                    lc.name,
                                    line.product_qty,
                                    pph.cost
                                
                                    FROM 
                                    purchase_cost_distribution_line as line
                                    LEFT JOIN purchase_cost_distribution as main on main.id = line.distribution
                                    LEFT JOIN mail_message as msg on msg.res_id = main.id and msg.model = 'purchase.cost.distribution'
                                    LEFT JOIN letter_credit as lc on lc.id = main.lc_id
                                    LEFT JOIN product_price_history as pph on pph.product_id = line.product_id and (pph.datetime = msg.date or pph.datetime + interval '10 seconds' = msg.date) 
                                    WHERE line.product_id = %s and pph.datetime is not null
                                    AND  main.id <= %s
                                
                                ) AS sub
                                GROUP BY main_id,cost_update,lc_number,unit_cost

                        """ % (product_id, landed_cost_id)
        self.env.cr.execute(cost_history_tbl_query)
        for row in self.env.cr.dictfetchall():
            history_table_data_list.append(row)
        return history_table_data_list

    def get_duty_tax_table_data(self, landed_cost_id, product_id):
        duty_tax_table_data_list = []

        duty_tax_tbl_query = """
                   select 
                        concat(aa.code,' ',aa.name) as acc_name,aml.id,aml.name,aml.debit
                        from 
                        purchase_cost_distribution_line_expense as line_child 
                        left join purchase_cost_distribution_line as line on line.id = line_child.distribution_line
                        left join purchase_cost_distribution as main on main.id = line.distribution
                        left join letter_credit as lc on lc.id = main.lc_id
                        left join account_analytic_account as aaa on aaa.id = lc.analytic_account_id
                        full join account_move_line as aml on (aml.account_id = line_child.account_id and aml.analytic_account_id = aaa.id)
                        left join account_account as aa on aa.id = line_child.account_id
                        left join ir_property ON (ir_property.value_reference = concat('account.account,', aa.id::text) AND ir_property.name = 'property_account_expense_id')
                        left join product_template as pt ON (ir_property.res_id = concat('product.template,', pt.id::text)) 
                        left join product_product as pp on pp.product_tmpl_id = pt.id
                                
                    where main.id = %s 
                    and line.product_id = %s
                    and pt.is_duty_tax = True 
                    and aml.debit != 0
                    group by acc_name,aml.id,aml.name,aml.debit
                """ % (landed_cost_id, product_id)
        self.env.cr.execute(duty_tax_tbl_query)
        for row in self.env.cr.dictfetchall():
            duty_tax_table_data_list.append(row)

        return duty_tax_table_data_list

    def generate_xlsx_report(self, workbook, data, obj):
        ReportUtility = self.env['report.utility']

        bold = workbook.add_format({'bold': True, 'size': 10})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#d4fff6'})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})

        th_cell_center = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_left = workbook.add_format(
            {'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # table body cell format
        td_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center_bold = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        td_cell_left_bold = workbook.add_format(
            {'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        td_cell_left_bold_color = workbook.add_format(
            {'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'fg_color': '#f2f2f2', 'border': 1})
        td_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_right_num = workbook.add_format(
            {'align': 'right', 'valign': 'vcenter', 'num_format': '#,###0.00', 'size': 10, 'border': 1})
        td_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_right_bold = workbook.add_format(
            {'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        td_cell_right_bold_num = workbook.add_format(
            {'num_format': '#,###0.00', 'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # WORKSHEET
        sheet = workbook.add_worksheet('LC Landed Cost Report')
        sheet.set_column('A:H', 12)
        sheet.merge_range(0, 0, 0, 7, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, 7, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, 7, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, 7, self.env.user.company_id.city + '-' + self.env.user.company_id.zip,
                          address_format)

        sheet.merge_range(4, 0, 4, 7, "LC Costing Report", name_format)
        sheet.merge_range(5, 0, 5, 1, "Currency", td_cell_left)
        sheet.merge_range(5, 2, 5, 3, obj.landed_cost_id.currency_id.name, td_cell_left)
        sheet.merge_range(6, 0, 6, 1, "LC Number", td_cell_left)
        sheet.merge_range(6, 2, 6, 3, obj.landed_cost_id.lc_id.name, td_cell_left)
        sheet.merge_range(7, 0, 7, 1, "Asset / Inventory GL", td_cell_left)
        sheet.merge_range(7, 2, 7, 3, obj.landed_cost_id.debit_account.name, td_cell_left)
        sheet.merge_range(8, 0, 8, 1, "Product Name", td_cell_left)
        sheet.merge_range(8, 2, 8, 3, obj.product_id.name, td_cell_left)

        sheet.merge_range(5, 4, 5, 5, "Date", td_cell_left)
        sheet.merge_range(5, 6, 5, 7, ReportUtility.get_date_from_string(obj.landed_cost_id.date), td_cell_left)
        sheet.merge_range(6, 4, 6, 5, "Operating Unit", td_cell_left)
        sheet.merge_range(6, 6, 6, 7, obj.landed_cost_id.operating_unit_id.name, td_cell_left)
        sheet.merge_range(7, 4, 7, 5, "Conversion Rate", td_cell_left)
        sheet.merge_range(7, 6, 7, 7, obj.landed_cost_id.currency_rate, td_cell_left)
        sheet.merge_range(8, 4, 8, 5, "Total Qty(kg)", td_cell_left)

        sheet.merge_range(10, 0, 10, 4, "Account", td_cell_left_bold_color)
        sheet.write(10, 5, "Amount", td_cell_left_bold_color)
        sheet.write(10, 6, "%", td_cell_left_bold_color)
        sheet.write(10, 7, "Unit Cost", td_cell_left_bold_color)

        main_table_data_list = self.get_main_table_data(obj.landed_cost_id.id, obj.product_id.id)
        row = 11
        sum_total_expense_amount_per_account = 0
        sum_amt_percentage = 0
        sum_total_cost_ratio_per_account = 0
        sum_total_cost_without_landed_cost = 0
        bucket = []
        product_qty_bucket = []
        sum_product_qty = 0

        for rec in main_table_data_list:
            sheet.merge_range(row, 0, row, 4, rec['acc_name'], td_cell_left)
            sheet.write(row, 5, rec['total_expense_amount_per_account'], td_cell_left)
            sheet.write(row, 6, rec['amt_percentage'], no_format)
            sheet.write(row, 7, rec['total_cost_ratio_per_account'], no_format)
            product_qty = rec['product_qty']
            if not rec['product_qty'] in product_qty_bucket:
                sum_product_qty = sum_product_qty + rec['product_qty']
            product_qty_bucket.append(product_qty)
            row += 1
            sum_total_expense_amount_per_account = sum_total_expense_amount_per_account + rec[
                'total_expense_amount_per_account']
            sum_amt_percentage = sum_amt_percentage + rec['amt_percentage']
            sum_total_cost_ratio_per_account = sum_total_cost_ratio_per_account + rec['total_cost_ratio_per_account']
            if not rec['total_cost_without_landed_cost'] in bucket:
                sum_total_cost_without_landed_cost = sum_total_cost_without_landed_cost + rec[
                    'total_cost_without_landed_cost']
            bucket.append(rec['total_cost_without_landed_cost'])

        sheet.merge_range(8, 6, 8, 7, sum_product_qty, td_cell_left)
        sheet.merge_range(row, 0, row, 4, "Total Landed Cost", td_cell_left_bold)
        sheet.write(row, 5, sum_total_expense_amount_per_account, td_cell_left_bold)
        sheet.write(row, 6, str('%.2f' % sum_amt_percentage) + " %", total_format)
        sheet.write(row, 7, sum_total_cost_ratio_per_account, total_format)
        row = row + 1
        sheet.merge_range(row, 0, row, 4, "Product Cost (BDT)", td_cell_left_bold)
        sheet.write(row, 5, sum_total_cost_without_landed_cost, td_cell_left_bold)
        sheet.write(row, 6, '%.2f' % (100 - sum_amt_percentage) + " %", total_format)
        total_unit_cost_ = 0
        if product_qty > 0:
            total_unit_cost_ = sum_total_cost_without_landed_cost / product_qty
        sheet.write(row, 7, total_unit_cost_, total_format)

        row = row + 1
        sheet.merge_range(row, 0, row, 4, "Total Product Cost (BDT)", td_cell_left_bold)
        sheet.write(row, 5, sum_total_expense_amount_per_account + sum_total_cost_without_landed_cost,
                    td_cell_left_bold)
        sheet.write(row, 6, str(100) + " %", total_format)
        sheet.write(row, 7, sum_total_cost_ratio_per_account + total_unit_cost_, total_format)
        row = row + 2
        sheet.merge_range(row, 0, row, 4, "Total Product Cost (USD)", td_cell_left_bold)
        sheet.write(row, 5, (
                    sum_total_expense_amount_per_account + sum_total_cost_without_landed_cost) / obj.landed_cost_id.currency_rate,
                    td_cell_left_bold)
        sheet.write(row, 6, " ", total_format)
        sheet.write(row, 7, (sum_total_cost_ratio_per_account + total_unit_cost_) / obj.landed_cost_id.currency_rate,
                    total_format)

        row = row + 2

        sheet.merge_range(row, 0, row, 3, "Cost Price History", td_cell_center_bold)
        sheet.merge_range(row, 5, row, 7, "Duty & Tax Details", td_cell_center_bold)
        row = row + 1
        sheet.write(row, 0, 'Cost Update', td_cell_left_bold)
        sheet.write(row, 1, 'LC Number', td_cell_left_bold)
        sheet.write(row, 2, 'Quantity', td_cell_left_bold)
        sheet.write(row, 3, 'Unit Cost', td_cell_left_bold)
        sheet.write(row, 5, 'Account', td_cell_left_bold)
        sheet.write(row, 6, 'Narration', td_cell_left_bold)
        sheet.write(row, 7, 'Amount', td_cell_left_bold)
        row = row + 1

        history_table_data_list = self.get_history_table_data(obj.landed_cost_id.id, obj.product_id.id)
        cost_price_history_start_row = row
        for rec in history_table_data_list:
            sheet.write(row, 0, ReportUtility.get_date_from_string(rec['cost_update']), td_cell_left)
            sheet.write(row, 1, rec['lc_number'], td_cell_left)
            sheet.write(row, 2, rec['product_qty'], td_cell_left)
            sheet.write(row, 3, rec['unit_cost'], no_format)

            row = row + 1

        duty_tax_table_data_list = self.get_duty_tax_table_data(obj.landed_cost_id.id, obj.product_id.id)
        # merge_range(row_from, col_from, row_to, col_to, value = "", format = nil)
        for rec in duty_tax_table_data_list:
            sheet.write(cost_price_history_start_row, 5, rec['acc_name'], td_cell_left)
            sheet.write(cost_price_history_start_row, 6, rec['name'], td_cell_left)
            sheet.write(cost_price_history_start_row, 7, rec['debit'], td_cell_left)

            cost_price_history_start_row = cost_price_history_start_row + 1


LandedCostInfoXLSX('report.purchase_landed_cost_extend.landed_cost_report_xlsx', 'landed.cost.report.wizard',
                   parser=report_sxw.rml_parse)
