from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
from odoo.tools import float_compare, float_round


GRP_ORDER = {
    0: 'net_revenue',
    1: 'cogs',
    2: 'depreciation',
    3: 'amortization',
    4: 'factory_overhead',
    5: 'gross_profit',
    6: 'indirect_income',
    7: 'profit_before_indirect_expense',
    8: 'indirect_expense',
    9: 'administrative',
    10: 'finance',
    11: 'marketing',
    12: 'distribution',
    13: 'net_profit'
}
GRP_NAME = {
    'net_revenue': 'Net Revenue',
    'cogs': 'Cost Of Goods Sold',
    'depreciation': 'Depreciation',
    'amortization': 'Amortization',
    'factory_overhead': 'Factory Overhead',
    'gross_profit': 'Gross Profit',
    'indirect_income': 'Indirect Incomes',
    'profit_before_indirect_expense': 'Profit Before Indirect Expenses',
    'indirect_expense': 'Indirect Expenses',
    'administrative': 'Administrative Expenses',
    'finance': 'Finance Expenses',
    'marketing': 'Marketing Expenses',
    'distribution': 'Distribution Expenses',
    'net_profit': 'Net Profit'
}
GRP_ACCOUNT_TAG = {
    'depreciation': 'NR-Depreciation',
    'amortization': 'NR-Amortization',
    'factory_overhead': 'NR-Factory Exp',
    'indirect_income': 'NR-Indirect Inc',
    'administrative': 'NR-Admin Exp',
    'finance': 'NR-Finance Exp',
    'marketing': 'NR-Marketing Exp',
    'distribution': 'NR-Dist Exp'
}
GRP_TOTAL_NAMES = ['gross_profit', 'profit_before_indirect_expense', 'indirect_expense', 'net_profit']


class ProfitLossWithRealizationXLSX(ReportXlsx):

    def _get_net_revenue(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        sql_str = """SELECT
                        cost_center_id,
                        name,
                        SUM(quantity) AS quantity,
                        SUM(amount) AS amount
                    FROM
                        ((SELECT
                            aml.cost_center_id,
                            acc.name,
                            0 AS product_id,
                            0 AS quantity,
                            -(SUM(aml.debit)-SUM(aml.credit)) AS amount
                        FROM
                            account_move_line aml
                            JOIN account_move mv ON mv.id=aml.move_id
                            JOIN account_account_account_tag aaat on aaat.account_account_id=aml.account_id
                            JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                            JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        """ + where_clause + """
                            AND aat.name IN ('Refund','Vat', 'Rental-Inc')
                        GROUP BY aml.cost_center_id,acc.name 
                        ORDER BY aml.cost_center_id)
                        UNION
                        (SELECT
                            aml.cost_center_id,
                            acc.name,
                            l.product_id,
                            CASE 
                                WHEN i.type='out_invoice' THEN
                                    CASE 
                                        WHEN COALESCE(p.ratio_in_percentage, 0)=0 THEN COALESCE(SUM(aml.quantity), 0)
                                        ELSE (p.ratio_in_percentage * COALESCE(SUM(aml.quantity), 0) / 100) 
                                    END
                                WHEN i.type='out_refund' and i.from_return = true THEN
                                    CASE 
                                        WHEN COALESCE(p.ratio_in_percentage, 0)=0 THEN (-1)*COALESCE(SUM(aml.quantity), 0)
                                        ELSE (-1)*(p.ratio_in_percentage * COALESCE(SUM(aml.quantity), 0) / 100) 
                                    END	
                                ELSE 0
                            END as quantity,
                            -(SUM(aml.debit)-SUM(aml.credit)) AS amount
                        FROM
                            account_move_line aml
                            JOIN account_move mv ON mv.id=aml.move_id
                            JOIN account_invoice i ON i.move_id=mv.id AND i.type IN ('out_invoice','out_refund')
                            JOIN account_invoice_line l ON l.invoice_id=i.id
                            JOIN product_product p ON p.id=l.product_id
                            JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        """ + where_clause + """
                        GROUP BY aml.cost_center_id,acc.name,l.product_id,p.ratio_in_percentage,i.type,i.from_return 
                        ORDER BY aml.cost_center_id)) AS tbl
                    GROUP BY cost_center_id,name
        """

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_cogs(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        if obj.cost_center_ids:
            cc_ids_str = ','.join(str(i) for i in obj.cost_center_ids.ids)
            where_clause += """ AND aml.account_id IN ((SELECT raw_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id IN (%s)) UNION
                                            (SELECT packing_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id IN (%s)))""" % (cc_ids_str, cc_ids_str)
        else:
            where_clause += """ AND aml.account_id IN ((SELECT raw_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id IS NOT NULL) UNION
                                                        (SELECT packing_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id IS NOT NULL))"""

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        COALESCE(SUM(aml.quantity), 0) AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                    """ + where_clause + """
                    GROUP BY aml.cost_center_id,acc.name
                    ORDER BY aml.cost_center_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_depreciation(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                        aa.id 
                                                    FROM 
                                                        account_account aa
                                                        JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                        JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                    WHERE
                                                        aat.name='%s' AND aa.company_id=%s)""" % (GRP_ACCOUNT_TAG['depreciation'], self.env.user.company_id.id)

        sql_str = """SELECT
                            aml.cost_center_id,
                            acc.name AS name,
                            COALESCE(SUM(aml.quantity), 0) AS quantity,
                            (SUM(aml.debit)-SUM(aml.credit)) AS amount
                        FROM
                            account_move_line aml
                            JOIN account_move mv ON mv.id=aml.move_id
                            JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        """ + where_clause + """
                        GROUP BY aml.cost_center_id,acc.name
                        ORDER BY aml.cost_center_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_amortization(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                        aa.id 
                                                    FROM 
                                                        account_account aa
                                                        JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                        JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                    WHERE
                                                        aat.name='%s' AND aa.company_id=%s)""" % (GRP_ACCOUNT_TAG['amortization'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        COALESCE(SUM(aml.quantity), 0) AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                    """ + where_clause + """
                    GROUP BY aml.cost_center_id,acc.name
                    ORDER BY aml.cost_center_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_factory_overhead(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                        aa.id 
                                                    FROM 
                                                        account_account aa
                                                        JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                        JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                    WHERE
                                                        aat.name='%s' AND aa.company_id=%s)""" % (GRP_ACCOUNT_TAG['factory_overhead'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        COALESCE(SUM(aml.quantity), 0) AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                    """ + where_clause + """
                    GROUP BY aml.cost_center_id,acc.name
                    ORDER BY aml.cost_center_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_indirect_income(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                        aa.id 
                                                    FROM 
                                                        account_account aa
                                                        JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                        JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                    WHERE
                                                        aat.name='%s' AND aa.company_id=%s)""" % (GRP_ACCOUNT_TAG['indirect_income'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        0 AS quantity,
                        -(SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.account_id,aa.name 
                    ORDER BY aml.account_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_administrative_expense(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                        aa.id 
                                                    FROM 
                                                        account_account aa
                                                        JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                        JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                    WHERE
                                                        aat.name='%s' AND aa.company_id=%s)""" % (GRP_ACCOUNT_TAG['administrative'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.cost_center_id,acc.name 
                    ORDER BY aml.cost_center_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_finance_expense(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                        aa.id 
                                                    FROM 
                                                        account_account aa
                                                        JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                        JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                    WHERE
                                                        aat.name='%s' AND aa.company_id=%s)""" % (GRP_ACCOUNT_TAG['finance'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.cost_center_id,acc.name 
                    ORDER BY aml.cost_center_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_marketing_expense(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                        aa.id 
                                                    FROM 
                                                        account_account aa
                                                        JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                        JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                    WHERE
                                                        aat.name='%s' AND aa.company_id=%s)""" % (GRP_ACCOUNT_TAG['marketing'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.cost_center_id,acc.name 
                    ORDER BY aml.cost_center_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def _get_distribution_expense(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                        aa.id 
                                                    FROM 
                                                        account_account aa
                                                        JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                        JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                    WHERE
                                                        aat.name='%s' AND aa.company_id=%s)""" % (GRP_ACCOUNT_TAG['distribution'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name AS name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                        JOIN account_account aa ON aa.id=aml.account_id
                    """ + where_clause + """ 
                    GROUP BY aml.cost_center_id,acc.name 
                    ORDER BY aml.cost_center_id"""

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            item_list.append(row)

        return item_list

    def finalize_comparison_table_data(self, item_list):
        for k in range(len(GRP_ORDER)):

            if GRP_ORDER[k] in GRP_TOTAL_NAMES:
                continue

            attr_name = 'cost_center_id'
            model_name = 'account.cost.center'
            if GRP_ORDER[k] == 'indirect_income':
                attr_name = 'account_id'
                model_name = 'account.account'

            unique_ids = set()
            for item in item_list:
                id_list = map(lambda x: x[attr_name], item[GRP_ORDER[k]])
                unique_ids.update(set(id_list))

            for item in item_list:
                temp_list = []
                id_list = map(lambda x: x[attr_name], item[GRP_ORDER[k]])
                diff_ids = unique_ids.difference(set(id_list))
                for d_id in list(diff_ids):
                    name = self.env[model_name].search([('id', '=', d_id)])[0].name
                    temp_list.append({attr_name: d_id, 'name': name, 'quantity': 0, 'amount': 0})

                if temp_list:
                    temp_list.extend(item[GRP_ORDER[k]])
                    item[GRP_ORDER[k]] = sorted(temp_list, key=lambda l: (l[attr_name], l['name']))

        return item_list

    def _get_query_where_clause(self, obj, date_from, date_to):
        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_ids:
            ou_params = ','.join(str(i) for i in obj.operating_unit_ids.ids)
            where_clause += " AND aml.operating_unit_id IN (%s)" % ou_params
        if obj.cost_center_ids:
            cc_params = ','.join(str(i) for i in obj.cost_center_ids.ids)
            where_clause += " AND aml.cost_center_id IN (%s)" % cc_params
        where_clause += " AND aml.company_id=%s" % self.env.user.company_id.id

        return where_clause

    @staticmethod
    def prepare_sales_quantity_vals(item_list):
        vals = {}
        for item in item_list:
            vals[item['cost_center_id']] = item['quantity']

        return vals

    @staticmethod
    def prepare_sales_amount_vals(item_list):
        vals = {}
        for item in item_list:
            vals[item['cost_center_id']] = item['amount']

        return vals

    @staticmethod
    def calc_on_sale(amount, net_revenue):
        on_sale = 0.0
        if net_revenue > 0:
            on_sale = (amount * 100) / net_revenue

        return on_sale

    @staticmethod
    def calc_group_total(item_dict):
        net_revenue = indirect_income = expense = indirect_expense = 0.0

        for key, item_list in item_dict.items():
            if key == 'net_revenue':
                net_revenue += float(sum(item['amount'] for item in item_list)) or 0.0
            elif key in ['cogs', 'depreciation', 'amortization', 'factory_overhead']:
                expense += float(sum(item['amount'] for item in item_list)) or 0.0
            elif key in ['administrative', 'finance', 'marketing', 'distribution']:
                indirect_expense += float(sum(item['amount'] for item in item_list)) or 0.0
            else:
                indirect_income += float(sum(item['amount'] for item in item_list)) or 0.0

        gross_profit = net_revenue - expense
        profit_before_indirect_expense = gross_profit + indirect_income
        net_profit = profit_before_indirect_expense - indirect_expense

        return {
            'gross_profit': gross_profit,
            'profit_before_indirect_expense': profit_before_indirect_expense,
            'indirect_expense': indirect_expense,
            'net_profit': net_profit
        }

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
        bold = workbook.add_format({'bold': True, 'size': 10})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

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

        if obj.cost_center_ids:
            cost_center_names_str = ', '.join(cc.name for cc in obj.cost_center_ids)
            sheet.merge_range(6, 0, 6, 1, "Cost Center: " + cost_center_names_str, bold)
        else:
            sheet.merge_range(6, 0, 6, 1, "Cost Center: All", bold)

        if obj.operating_unit_ids:
            operating_unit_names_str = ', '.join(ou.name for ou in obj.operating_unit_ids)
            sheet.merge_range(6, 3, 6, 4, "Operating Unit: " + operating_unit_names_str, bold)
        else:
            sheet.merge_range(6, 3, 6, 4, "Operating Unit: All", bold)

        # TABLE HEADER
        row, col = 8, 0
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
            nr_item_list = value.get('net_revenue', [])
            net_revenue = sum(float(item['amount']) for item in nr_item_list)
            group_total_dict = self.calc_group_total(value)
            cc_wise_sales_qty_dict = self.prepare_sales_quantity_vals(nr_item_list)
            cc_wise_sales_amount_dict = self.prepare_sales_amount_vals(nr_item_list)

            for k in range(len(GRP_ORDER)):
                # GROUP TOTAL ROW
                if GRP_ORDER[k] in GRP_TOTAL_NAMES:
                    grp_amount = group_total_dict.get(GRP_ORDER[k], 0)
                    grp_on_sale = self.calc_on_sale(grp_amount, net_revenue)

                    if index == 0:
                        sheet.write(row, col, GRP_NAME[GRP_ORDER[k]], td_cell_left_bold)
                    sheet.write(row, col + 1, '', td_cell_center)
                    sheet.write(row, col + 2, '', td_cell_center)
                    sheet.write(row, col + 3, float_round(grp_amount, precision_digits=2), total_format)
                    sheet.write(row, col + 4, float_round(grp_on_sale, precision_digits=2), total_format)
                    row += 1
                    continue
                # GROUP TOTAL ROW

                item_list = value.get(GRP_ORDER[k])
                # sorted list
                item_list = sorted(item_list, key=lambda i: i['name'])

                # PARENT ROW
                pr_amount = float(sum(item['amount'] for item in item_list)) or 0.0
                pr_on_sale = self.calc_on_sale(pr_amount, net_revenue)

                if index == 0:
                    sheet.write(row, col, GRP_NAME[GRP_ORDER[k]], td_cell_left_bold)
                sheet.write(row, col + 1, '', td_cell_center)
                sheet.write(row, col + 2, '', td_cell_center)
                sheet.write(row, col + 3, float_round(pr_amount, precision_digits=2), total_format)
                sheet.write(row, col + 4, float_round(pr_on_sale, precision_digits=2), total_format)
                row += 1
                # PARENT ROW

                # CHILD ROW
                for item in item_list:
                    sales_amount = net_revenue
                    if 'cost_center_id' in item and GRP_ORDER[k] != 'net_revenue':
                        sales_amount = cc_wise_sales_amount_dict.get(item['cost_center_id'], 0.0)

                    ch_qty = cc_wise_sales_qty_dict.get(item['cost_center_id'], 0.0) if 'cost_center_id' in item else item['quantity']
                    ch_amount = float(item['amount']) or 0.0
                    ch_net_realization = (ch_amount / ch_qty) if ch_qty > 0 else 0.0
                    ch_on_sale = self.calc_on_sale(ch_amount, sales_amount)

                    if index == 0:
                        sheet.write(row, col, '         ' + item['name'], td_cell_left)
                    sheet.write(row, col + 1, float_round(ch_qty, precision_digits=2), no_format)
                    sheet.write(row, col + 2, float_round(ch_net_realization, precision_digits=2), no_format)
                    sheet.write(row, col + 3, float_round(ch_amount, precision_digits=3), no_format)
                    sheet.write(row, col + 4, float_round(ch_on_sale, precision_digits=2), no_format)
                    row += 1
                # CHILD ROW

            # SET STARTING ROW,COLUMN FOR COMPARISON
            row = 10
            col += 5


ProfitLossWithRealizationXLSX('report.samuda_account_reports.profit_loss_with_realization_xlsx', 'profit.loss.realization.wizard', parser=report_sxw.rml_parse)
