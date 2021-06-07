from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
from odoo.tools import float_compare, float_round

IE_ORDER = {
    0: 'net_revenue',
    1: 'cogs',
    2: 'depreciation',
    3: 'amortization',
    4: 'factory_overhead',
    5: 'indirect_income',
    6: 'administrative',
    7: 'finance',
    8: 'marketing',
    9: 'distribution'
}
IE_NAME = {
    'net_revenue': 'Net Revenue',
    'cogs': 'Cost Of Goods Sold',
    'depreciation': 'Depreciation',
    'amortization': 'Amortization',
    'factory_overhead': 'Factory Overhead',
    'indirect_income': 'Indirect Incomes',
    'administrative': 'Administrative Expenses',
    'finance': 'Finance Expenses',
    'marketing': 'Marketing Expenses',
    'distribution': 'Distribution Expenses'
}
IE_ACCOUNT = {
    'depreciation': 5601,
    'amortization': 5602,
    'factory_overhead': 5527,
    'indirect_income': 4316,
    'administrative': 5815,
    'finance': 5890,
    'marketing': 5929,
    'distribution': 5100
}
EXPENSE = ['cogs', 'depreciation', 'amortization', 'factory_overhead']
INDIRECT_EXPENSE = ['administrative', 'finance', 'marketing', 'distribution']
INCOME_USER_TYPE_ID = 14


class ProfitLossWithRealizationXLSX(ReportXlsx):

    def _get_net_revenue(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        account_ids = self.env['account.account'].search([('user_type_id', '=', INCOME_USER_TYPE_ID)]).ids
        if account_ids:
            param = (tuple(account_ids),)
            where_clause += " AND aml.account_id IN %s" % param

        _net_revenue_sql_str = """SELECT
                                    aml.cost_center_id,
                                    acc.name AS name,
                                    COALESCE(SUM(aml.quantity), 0) AS quantity,
                                    -(SUM(aml.debit)-SUM(aml.credit)) AS amount
                                FROM
                                    account_move_line aml
                                    JOIN account_move mv ON mv.id=aml.move_id
                                    JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                                """ + where_clause + """ GROUP BY aml.cost_center_id,acc.name 
                                ORDER BY aml.cost_center_id"""

        cr.execute(_net_revenue_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_cogs(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        if obj.cost_center_id:
            where_clause += """ AND aml.account_id IN ((SELECT raw_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id=%s) UNION
                                            (SELECT packing_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id=%s))""" % (obj.cost_center_id.id, obj.cost_center_id.id)
        else:
            where_clause += """ AND aml.account_id IN ((SELECT raw_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id IS NOT NULL) UNION
                                                        (SELECT packing_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id IS NOT NULL))"""

        _sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        COALESCE(SUM(aml.quantity), 0) AS quantity,
                        ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                    """ + where_clause + """
                    GROUP BY aml.cost_center_id,acc.name
                    ORDER BY aml.cost_center_id"""
        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_depreciation(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (IE_ACCOUNT['depreciation'], self.env.user.company_id.id, IE_ACCOUNT['depreciation'], self.env.user.company_id.id)

        _sql_str = """SELECT
                            aml.cost_center_id,
                            acc.name AS name,
                            COALESCE(SUM(aml.quantity), 0) AS quantity,
                            ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                        FROM
                            account_move_line aml
                            JOIN account_move mv ON mv.id=aml.move_id
                            JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        """ + where_clause + """
                        GROUP BY aml.cost_center_id,acc.name
                        ORDER BY aml.cost_center_id"""
        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_amortization(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (IE_ACCOUNT['amortization'], self.env.user.company_id.id, IE_ACCOUNT['amortization'], self.env.user.company_id.id)

        _sql_str = """SELECT
                            aml.cost_center_id,
                            acc.name AS name,
                            COALESCE(SUM(aml.quantity), 0) AS quantity,
                            ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                        FROM
                            account_move_line aml
                            JOIN account_move mv ON mv.id=aml.move_id
                            JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        """ + where_clause + """
                        GROUP BY aml.cost_center_id,acc.name
                        ORDER BY aml.cost_center_id"""
        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_factory_overhead(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (IE_ACCOUNT['factory_overhead'], self.env.user.company_id.id, IE_ACCOUNT['factory_overhead'], self.env.user.company_id.id)

        _sql_str = """SELECT
                            aml.cost_center_id,
                            acc.name AS name,
                            COALESCE(SUM(aml.quantity), 0) AS quantity,
                            ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                        FROM
                            account_move_line aml
                            JOIN account_move mv ON mv.id=aml.move_id
                            JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        """ + where_clause + """
                        GROUP BY aml.cost_center_id,acc.name
                        ORDER BY aml.cost_center_id"""

        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_indirect_income(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (IE_ACCOUNT['indirect_income'], self.env.user.company_id.id, IE_ACCOUNT['indirect_income'], self.env.user.company_id.id)

        _sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        0 AS quantity,
                        ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.account_id,aa.name 
                    ORDER BY aml.account_id"""
        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_administrative_expense(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (IE_ACCOUNT['administrative'], self.env.user.company_id.id, IE_ACCOUNT['administrative'], self.env.user.company_id.id)

        _sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        0 AS quantity,
                        ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.cost_center_id,acc.name 
                    ORDER BY aml.cost_center_id"""
        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_finance_expense(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (IE_ACCOUNT['finance'], self.env.user.company_id.id, IE_ACCOUNT['finance'], self.env.user.company_id.id)

        _sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        0 AS quantity,
                        ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.cost_center_id,acc.name 
                    ORDER BY aml.cost_center_id"""
        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_marketing_expense(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (IE_ACCOUNT['marketing'], self.env.user.company_id.id, IE_ACCOUNT['marketing'], self.env.user.company_id.id)

        _sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        0 AS quantity,
                        ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.cost_center_id,acc.name 
                    ORDER BY aml.cost_center_id"""
        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def _get_distribution_expense(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (IE_ACCOUNT['distribution'], self.env.user.company_id.id, IE_ACCOUNT['distribution'], self.env.user.company_id.id)

        _sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        0 AS quantity,
                        ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.cost_center_id,acc.name 
                    ORDER BY aml.cost_center_id"""
        cr.execute(_sql_str)
        for row in cr.dictfetchall():
            data_list.append(row)

        return data_list

    def finalize_comparison_table_data(self, data_list):
        for n in range(len(IE_ORDER)):
            attr_name = 'cost_center_id'
            model_name = 'account.cost.center'
            if IE_ORDER[n] == 'indirect_income':
                attr_name = 'account_id'
                model_name = 'account.account'

            unique_ids = set()
            for item in data_list:
                id_list = map(lambda x: x[attr_name], item[IE_ORDER[n]])
                unique_ids.update(set(id_list))

            for item in data_list:
                temp_list = []
                id_list = map(lambda x: x[attr_name], item[IE_ORDER[n]])
                diff_ids = unique_ids.difference(set(id_list))
                for d_id in list(diff_ids):
                    name = self.env[model_name].search([('id', '=', d_id)])[0].name
                    temp_list.append({attr_name: d_id, 'name': name, 'quantity': 0, 'amount': 0})

                if temp_list:
                    temp_list.extend(item[IE_ORDER[n]])
                    item[IE_ORDER[n]] = sorted(temp_list, key=lambda l: (l[attr_name], l['name']))

        return data_list

    def _get_query_where_clause(self, obj, date_from, date_to):
        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id
        where_clause += " AND aml.company_id=%s" % self.env.user.company_id.id

        return where_clause

    @staticmethod
    def get_net_sales_qty_vals(data_list):
        net_sales_qty_vals = {}
        for item in data_list:
            net_sales_qty_vals[item['cost_center_id']] = item['quantity']

        return net_sales_qty_vals

    @staticmethod
    def get_net_sales_amount_vals(data_list):
        net_sales_amount_vals = {}
        for item in data_list:
            net_sales_amount_vals[item['cost_center_id']] = item['amount']

        return net_sales_amount_vals

    @staticmethod
    def calc_income_expense(data_dict):
        income_expense_vals = {}
        for _, value in IE_ORDER.items():
            d_list = data_dict.get(value)
            income_expense_vals[value] = float(sum(item['amount'] for item in d_list)) or 0.0

        return income_expense_vals

    @staticmethod
    def calc_profit(income_expense_vals):
        expense = indirect_expense = 0.0
        net_revenue = income_expense_vals.get('net_revenue')
        indirect_income = income_expense_vals.get('indirect_income')
        for key, value in income_expense_vals.items():
            if key in EXPENSE:
                expense += value
            elif key in INDIRECT_EXPENSE:
                indirect_expense += value
            else:
                pass

        gross_profit = net_revenue - expense
        profit_before_indirect_expense = gross_profit + indirect_income
        net_profit = profit_before_indirect_expense - indirect_expense

        return gross_profit, profit_before_indirect_expense, net_profit

    @staticmethod
    def calc_on_sale(amount, net_revenue):
        on_sale = 0.0
        if net_revenue > 0:
            on_sale = float_round((amount * 100) / net_revenue, precision_digits=3)

        return on_sale

    def generate_xlsx_report(self, workbook, data, obj):
        report_data = []
        comparison_table = obj.get_periods()
        for tbl in comparison_table:
            temp_dict = {}
            temp_dict['net_revenue'] = self._get_net_revenue(obj, tbl[0], tbl[1])
            temp_dict['cogs'] = self._get_cogs(obj, tbl[0], tbl[1])
            temp_dict['depreciation'] = self._get_depreciation(obj, tbl[0], tbl[1])
            temp_dict['amortization'] = self._get_amortization(obj, tbl[0], tbl[1])
            temp_dict['factory_overhead'] = self._get_factory_overhead(obj, tbl[0], tbl[1])
            temp_dict['indirect_income'] = self._get_indirect_income(obj, tbl[0], tbl[1])
            temp_dict['administrative'] = self._get_administrative_expense(obj, tbl[0], tbl[1])
            temp_dict['finance'] = self._get_finance_expense(obj, tbl[0], tbl[1])
            temp_dict['marketing'] = self._get_marketing_expense(obj, tbl[0], tbl[1])
            temp_dict['distribution'] = self._get_distribution_expense(obj, tbl[0], tbl[1])
            report_data.append(temp_dict)

        if obj.comparison:
            report_data = self.finalize_comparison_table_data(report_data)

        # FORMAT
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})

        # table header cell format
        th_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        th_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # table body cell format
        td_cell_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10, 'border': 1})
        td_cell_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'size': 10, 'border': 1})

        td_cell_left_bold = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        td_cell_center_bold = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})
        td_cell_right_bold = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 10, 'border': 1})

        # WORKSHEET
        sheet = workbook.add_worksheet('Profit and Loss with realization')

        # SET CELL WIDTH
        col = 0
        for index, _ in enumerate(comparison_table):
            if index == 0:
                sheet.set_column(col, col, 50)
            sheet.set_column(col + 1, col + 1, 10)
            sheet.set_column(col + 2, col + 2, 18)
            sheet.set_column(col + 3, col + 3, 20)
            sheet.set_column(col + 4, col + 4, 15)
            col += 5

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, 4, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, 4, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, 4, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, 4, self.env.user.company_id.city + '-' + self.env.user.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, 4, "Statement of Comprehensive Income", name_format)

        # TABLE HEADER
        row, col = 5, 0
        for index, value in enumerate(comparison_table):
            if index == 0:
                sheet.write(row, col, '', th_cell_center)
            sheet.merge_range(row, col + 1, row, col + 4, obj.get_full_date_names(value[1], value[0]), th_cell_center)
            col += 5

        row += 1
        col = 0
        for index, _ in enumerate(comparison_table):
            if index == 0:
                sheet.write(row, col, 'Particulars', th_cell_center)
            sheet.write(row, col + 1, 'Sales in MT.', th_cell_center)
            sheet.write(row, col + 2, 'Net realization in MT.', th_cell_center)
            sheet.write(row, col + 3, 'Amount (BDT)', th_cell_center)
            sheet.write(row, col + 4, 'On Sales (%)', th_cell_center)
            col += 5

        # TABLE BODY
        row += 1
        col = 0
        for index, value in enumerate(report_data):
            income_expense_vals = self.calc_income_expense(value)
            net_revenue = income_expense_vals.get('net_revenue')
            gross_profit, profit_before_indirect_expense, net_profit = self.calc_profit(income_expense_vals)
            net_sales_qty_vals = {}
            net_sales_amount_vals = {}

            for n in range(len(IE_ORDER)):
                data_list = value.get(IE_ORDER[n])
                amount_total = income_expense_vals.get(IE_ORDER[n])
                net_sales_qty_vals = self.get_net_sales_qty_vals(data_list) if IE_ORDER[n] == 'net_revenue' else net_sales_qty_vals
                net_sales_amount_vals = self.get_net_sales_amount_vals(data_list) if IE_ORDER[n] == 'net_revenue' else net_sales_amount_vals

                # gross profit row
                if IE_ORDER[n] == 'indirect_income':
                    on_sale = self.calc_on_sale(gross_profit, net_revenue)
                    gross_profit = formatLang(self.env, float_round(gross_profit, precision_digits=3))

                    if index == 0:
                        sheet.write(row, col, 'Gross Profit', td_cell_left_bold)
                    sheet.write(row, col + 1, '', td_cell_center)
                    sheet.write(row, col + 2, '', td_cell_center)
                    sheet.write(row, col + 3, gross_profit, td_cell_right_bold)
                    sheet.write(row, col + 4, on_sale, td_cell_right_bold)
                    row += 1

                # income, expense parent row
                on_sale = self.calc_on_sale(amount_total, net_revenue)
                amount_total = formatLang(self.env, float_round(amount_total, precision_digits=3))

                if index == 0:
                    sheet.write(row, col, IE_NAME[IE_ORDER[n]], td_cell_left_bold)
                sheet.write(row, col + 1, '', td_cell_center)
                sheet.write(row, col + 2, '', td_cell_center)
                sheet.write(row, col + 3, amount_total, td_cell_right_bold)
                sheet.write(row, col + 4, on_sale, td_cell_right_bold)
                row += 1

                # child row
                for item in data_list:
                    qty = item['quantity']
                    if IE_ORDER[n] != 'indirect_income':
                        qty = net_sales_qty_vals.get(item['cost_center_id']) or qty

                    net_realization = float(item['amount'] / qty) if qty > 0 else 0.0
                    # on_sale = self.calc_on_sale(float(item['amount']), net_revenue)

                    # on sale calculation
                    if IE_ORDER[n] == 'net_revenue':
                        on_sale = self.calc_on_sale(float(item['amount']), net_revenue)
                    elif IE_ORDER[n] == 'indirect_income':
                        on_sale = 0
                        if obj.cost_center_id:
                            on_sale = self.calc_on_sale(float(item['amount']), net_revenue)
                    else:
                        on_sale = self.calc_on_sale(float(item['amount']), net_sales_amount_vals.get(item['cost_center_id'], 0))

                    if index == 0:
                        sheet.write(row, col, '         ' + item['name'], td_cell_left)
                    sheet.write(row, col + 1, float_round(float(qty), precision_digits=3), td_cell_right)
                    sheet.write(row, col + 2, float_round(net_realization, precision_digits=3), td_cell_right)
                    sheet.write(row, col + 3, formatLang(self.env, float_round(float(item['amount']), precision_digits=3)), td_cell_right)
                    sheet.write(row, col + 4, on_sale, td_cell_right)
                    row += 1

                # profit before indirect expenses row
                if IE_ORDER[n] == 'indirect_income':
                    on_sale = self.calc_on_sale(profit_before_indirect_expense, net_revenue)
                    profit_before_indirect_expense = formatLang(self.env, float_round(profit_before_indirect_expense, precision_digits=3))

                    if index == 0:
                        sheet.write(row, col, 'Profit Before Indirect Expenses', td_cell_left_bold)
                    sheet.write(row, col + 1, '', td_cell_center)
                    sheet.write(row, col + 2, '', td_cell_center)
                    sheet.write(row, col + 3, profit_before_indirect_expense, td_cell_right_bold)
                    sheet.write(row, col + 4, on_sale, td_cell_right_bold)
                    row += 1

                    # inderect expense row
                    indirect_expense_amount_total = sum(income_expense_vals[e] for e in INDIRECT_EXPENSE)
                    on_sale = self.calc_on_sale(indirect_expense_amount_total, net_revenue)
                    indirect_expense_amount_total = formatLang(self.env, float_round(indirect_expense_amount_total, precision_digits=3))

                    if index == 0:
                        sheet.write(row, col, 'Indirect Expenses', td_cell_left_bold)
                    sheet.write(row, col + 1, '', td_cell_center)
                    sheet.write(row, col + 2, '', td_cell_center)
                    sheet.write(row, col + 3, indirect_expense_amount_total, td_cell_right_bold)
                    sheet.write(row, col + 4, on_sale, td_cell_right_bold)
                    row += 1

            # net profit row
            on_sale = self.calc_on_sale(net_profit, net_revenue)
            net_profit = formatLang(self.env, float_round(net_profit, precision_digits=3))

            if index == 0:
                sheet.write(row, col, 'Net Profit', td_cell_left_bold)
            sheet.write(row, col + 1, '', td_cell_center)
            sheet.write(row, col + 2, '', td_cell_center)
            sheet.write(row, col + 3, net_profit, td_cell_right_bold)
            sheet.write(row, col + 4, on_sale, td_cell_right_bold)

            # set starting row for comparison
            row = 7
            col += 5


ProfitLossWithRealizationXLSX('report.samuda_account_reports.profit_loss_with_realization_xlsx', 'profit.loss.realization.wizard', parser=report_sxw.rml_parse)
