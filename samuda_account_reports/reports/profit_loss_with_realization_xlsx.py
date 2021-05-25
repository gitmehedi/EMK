from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
from odoo.tools import float_compare, float_round


INCOME_EXPENSE_SEQUENCE = {
    0: 'net_revenue',
    1: 'cogs',
    2: 'depreciation',
    3: 'amortization',
    4: 'factory_overhead',
    5: 'indirect_income',
    6: 'indirect_expense'
}
INCOME_EXPENSE_STRING = {
    'net_revenue': 'Net Revenue',
    'cogs': 'Cost Of Goods Sold',
    'depreciation': 'Depreciation',
    'amortization': 'Amortization',
    'factory_overhead': 'Factory Overhead',
    'indirect_income': 'Indirect Incomes',
    'indirect_expense': 'Indirect Expenses'
}
INCOME_EXPENSE_ACCOUNT_CODE = {
    'depreciation': 5601,
    'amortization': 5602,
    'factory_overhead': 5527,
    'indirect_income': 4316
}

INDIRECT_EXPENSE_SEQUENCE = {
    0: 'administrative',
    1: 'finance',
    2: 'marketing',
    3: 'distribution'
}
INDIRECT_EXPENSE_STRING = {
    'administrative': 'Administrative Expenses',
    'finance': 'Finance Expenses',
    'marketing': 'Marketing Expenses',
    'distribution': 'Distribution Expenses'
}
INDIRECT_EXPENSE_ACCOUNT_CODE = {
    'administrative': 5815,
    'finance': 5890,
    'marketing': 5929,
    'distribution': 5100
}


class ProfitLossWithRealizationXLSX(ReportXlsx):

    def prepare_comparison_data(self, report_data):
        for n in range(len(INCOME_EXPENSE_SEQUENCE)):
            if INCOME_EXPENSE_SEQUENCE[n] == 'indirect_expense':
                for s in range(len(INDIRECT_EXPENSE_SEQUENCE)):
                    cost_center_ids = set()
                    for exp_data in report_data:
                        cc_ids = map(lambda x: x['cost_center_id'], exp_data[INCOME_EXPENSE_SEQUENCE[n]][INDIRECT_EXPENSE_SEQUENCE[s]])
                        cost_center_ids.update(set(cc_ids))

                    for exp_data in report_data:
                        d_list = []
                        cc_ids = map(lambda x: x['cost_center_id'], exp_data[INCOME_EXPENSE_SEQUENCE[n]][INDIRECT_EXPENSE_SEQUENCE[s]])
                        diff_ids = cost_center_ids.difference(set(cc_ids))
                        for cc_id in list(diff_ids):
                            cc_name = self.env['account.cost.center'].search([('id', '=', cc_id)])[0].name
                            d_list.append({'cost_center_id': cc_id, 'name': cc_name, 'quantity': 0, 'amount': 0})
                        if d_list:
                            d_list.extend(exp_data[INCOME_EXPENSE_SEQUENCE[n]][INDIRECT_EXPENSE_SEQUENCE[s]])
                            exp_data[INCOME_EXPENSE_SEQUENCE[n]][INDIRECT_EXPENSE_SEQUENCE[s]] = sorted(d_list, key=lambda l: (l['cost_center_id'], l['name']))
            else:
                key = 'account_id' if INCOME_EXPENSE_SEQUENCE[n] == 'indirect_income' else 'cost_center_id'
                model = 'account.account' if INCOME_EXPENSE_SEQUENCE[n] == 'indirect_income' else 'account.cost.center'
                unique_ids = set()
                for data in report_data:
                    ids = map(lambda x: x[key], data[INCOME_EXPENSE_SEQUENCE[n]])
                    unique_ids.update(set(ids))

                for data in report_data:
                    d_list = []
                    ids = map(lambda x: x[key], data[INCOME_EXPENSE_SEQUENCE[n]])
                    diff_ids = unique_ids.difference(set(ids))
                    for d_id in list(diff_ids):
                        name = self.env[model].search([('id', '=', d_id)])[0].name
                        d_list.append({key: d_id, 'name': name, 'quantity': 0, 'amount': 0})
                    if d_list:
                        d_list.extend(data[INCOME_EXPENSE_SEQUENCE[n]])
                        data[INCOME_EXPENSE_SEQUENCE[n]] = sorted(d_list, key=lambda l: (l[key], l['name']))

        return report_data

    def _get_net_revenue(self, obj, date_from, date_to):
        vat_refund_data_list = []
        data_list = []
        cr = self.env.cr

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        _total_vat_refund_sql_str = """SELECT
                                            aml.cost_center_id,
                                            acc.name AS name,
                                            ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                                        FROM
                                            account_move_line aml
                                            JOIN account_move mv ON mv.id=aml.move_id
                                            JOIN account_account_account_tag aaat ON aaat.account_account_id=aml.account_id
                                            JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                            JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                                        """ + where_clause + """ AND aat.name IN ('Sales-Vat','Sales-Refund')
                                        GROUP BY aml.cost_center_id,acc.name ORDER BY aml.cost_center_id"""

        cr.execute(_total_vat_refund_sql_str)
        for row in cr.dictfetchall():
            vat_refund_data_list.append(row)

        account_ids = []
        if obj.cost_center_id:
            product_templates = self.env['product.template'].search([('cost_center_id', '=', obj.cost_center_id.id), ('sale_ok', '=', True), ('active', '=', True)])
            account_ids.extend(product_templates.mapped('property_account_income_id').ids)
            account_ids.extend(product_templates.mapped('sale_type_account_ids').mapped('account_id').ids)
        else:
            product_templates = self.env['product.template'].search([('cost_center_id', '!=', 'null'), ('sale_ok', '=', True), ('active', '=', True)])
            account_ids.extend(product_templates.mapped('property_account_income_id').ids)
            account_ids.extend(product_templates.mapped('sale_type_account_ids').mapped('account_id').ids)

        if account_ids:
            param = (tuple(account_ids),)
            where_clause += " AND aml.account_id IN %s" % param

        _total_sales_sql_str = """SELECT
                                    aml.cost_center_id,
                                    acc.name AS name,
                                    COALESCE(SUM(aml.quantity), 0) AS quantity,
                                    ABS(SUM(aml.debit)-SUM(aml.credit)) AS amount
                                FROM
                                    account_move_line aml
                                    JOIN account_move mv ON mv.id=aml.move_id
                                    JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                                """ + where_clause + """ GROUP BY aml.cost_center_id,acc.name 
                                ORDER BY aml.cost_center_id"""

        cr.execute(_total_sales_sql_str)
        for row in cr.dictfetchall():
            vat_refund_line = filter(lambda x: x['cost_center_id'] == row['cost_center_id'], vat_refund_data_list)
            if vat_refund_line:
                amount = row['amount'] - vat_refund_line[0]['amount']
                row['amount'] = amount

            data_list.append(row)

        return data_list

    def _get_cogs(self, obj, date_from, date_to):
        data_list = []
        cr = self.env.cr

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id
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

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (INCOME_EXPENSE_ACCOUNT_CODE['depreciation'], self.env.user.company_id.id, INCOME_EXPENSE_ACCOUNT_CODE['depreciation'], self.env.user.company_id.id)

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

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (INCOME_EXPENSE_ACCOUNT_CODE['amortization'], self.env.user.company_id.id, INCOME_EXPENSE_ACCOUNT_CODE['amortization'], self.env.user.company_id.id)

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

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (INCOME_EXPENSE_ACCOUNT_CODE['factory_overhead'], self.env.user.company_id.id, INCOME_EXPENSE_ACCOUNT_CODE['factory_overhead'], self.env.user.company_id.id)

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

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (INCOME_EXPENSE_ACCOUNT_CODE['indirect_income'], self.env.user.company_id.id, INCOME_EXPENSE_ACCOUNT_CODE['indirect_income'], self.env.user.company_id.id)

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

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (INDIRECT_EXPENSE_ACCOUNT_CODE['administrative'], self.env.user.company_id.id, INDIRECT_EXPENSE_ACCOUNT_CODE['administrative'], self.env.user.company_id.id)

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

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (INDIRECT_EXPENSE_ACCOUNT_CODE['finance'], self.env.user.company_id.id, INDIRECT_EXPENSE_ACCOUNT_CODE['finance'], self.env.user.company_id.id)

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

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (INDIRECT_EXPENSE_ACCOUNT_CODE['marketing'], self.env.user.company_id.id, INDIRECT_EXPENSE_ACCOUNT_CODE['marketing'], self.env.user.company_id.id)

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

        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        where_clause += """ AND aml.account_id IN ((SELECT ac.id FROM account_account ac 
                                        JOIN account_account asp ON asp.id=ac.parent_id JOIN account_account ap ON ap.id=asp.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s)
                                        UNION (SELECT ac.id FROM account_account ac JOIN account_account ap ON ap.id=ac.parent_id 
                                        WHERE ap.id=%s AND ac.internal_type!='view' AND ac.company_id=%s))""" % (INDIRECT_EXPENSE_ACCOUNT_CODE['distribution'], self.env.user.company_id.id, INDIRECT_EXPENSE_ACCOUNT_CODE['distribution'], self.env.user.company_id.id)

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

    def _get_indirect_expense(self, obj, date_from, date_to):
        expense_dict = {}
        expense_dict['administrative'] = self._get_administrative_expense(obj, date_from, date_to)
        expense_dict['finance'] = self._get_finance_expense(obj, date_from, date_to)
        expense_dict['marketing'] = self._get_marketing_expense(obj, date_from, date_to)
        expense_dict['distribution'] = self._get_distribution_expense(obj, date_from, date_to)

        return expense_dict

    @staticmethod
    def calculate_profit(data_dict):
        net_revenue = cogs = depreciation = amortization = factory_overhead = indirect_income = indirect_expense = 0.0

        revenue_data_list = data_dict.get('net_revenue')
        cogs_data_list = data_dict.get('cogs')
        depreciation_data_list = data_dict.get('depreciation')
        amortization_data_list = data_dict.get('amortization')
        factory_overhead_data_list = data_dict.get('factory_overhead')
        indirect_income_data_list = data_dict.get('indirect_income')
        indirect_expense_data_dict = data_dict.get('indirect_expense')

        net_revenue += float(sum(item['amount'] for item in revenue_data_list))
        cogs += float(sum(item['amount'] for item in cogs_data_list))
        depreciation += float(sum(item['amount'] for item in depreciation_data_list))
        amortization += float(sum(item['amount'] for item in amortization_data_list))
        factory_overhead += float(sum(item['amount'] for item in factory_overhead_data_list))
        indirect_income += float(sum(item['amount'] for item in indirect_income_data_list))

        for expense_data_list in indirect_expense_data_dict.values():
            indirect_expense += float(sum(item['amount'] for item in expense_data_list))

        gross_profit = net_revenue - cogs - depreciation - amortization - factory_overhead
        profit_before_indirect_expense = gross_profit + indirect_income
        net_profit = profit_before_indirect_expense - indirect_expense

        amount_dict = {
            'net_revenue': net_revenue,
            'cogs': cogs,
            'depreciation': depreciation,
            'amortization': amortization,
            'factory_overhead': factory_overhead,
            'indirect_income': indirect_income,
            'indirect_expense': indirect_expense
        }

        return gross_profit, profit_before_indirect_expense, net_profit, net_revenue, amount_dict

    @staticmethod
    def _get_query_where_clause(obj, date_from, date_to):
        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id
        if obj.cost_center_id:
            where_clause += " AND aml.cost_center_id=%s" % obj.cost_center_id.id

        return where_clause

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
            temp_dict['indirect_expense'] = self._get_indirect_expense(obj, tbl[0], tbl[1])
            report_data.append(temp_dict)
            # for n in range(len(comparison_table) - 1):
            #     report_data.append(temp_dict)
            # break

        report_data = self.prepare_comparison_data(report_data)

        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        font_10 = workbook.add_format({'size': 10})
        font_12 = workbook.add_format({'bold': True, 'size': 12})
        no_format = workbook.add_format({'num_format': '#,###0.00', 'size': 10, 'border': 1})
        total_format = workbook.add_format({'num_format': '#,###0.00', 'bold': True, 'size': 10, 'border': 1})

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
        sheet = workbook.add_worksheet('Income Statement')

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
            # sheet.merge_range(row, col + 1, row, col + 4, 'January 2021', th_cell_center)
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
        for index, r_data in enumerate(report_data):
            gross_profit, profit_before_indirect_expense, net_profit, net_revenue, amount_dict = self.calculate_profit(r_data)

            for s in range(len(INCOME_EXPENSE_SEQUENCE)):
                val = r_data.get(INCOME_EXPENSE_SEQUENCE[s])
                amount = amount_dict.get(INCOME_EXPENSE_SEQUENCE[s])

                # gross profit row
                if INCOME_EXPENSE_SEQUENCE[s] == 'indirect_income':
                    if index == 0:
                        sheet.write(row, col, 'Gross Profit', td_cell_left_bold)
                    sheet.write(row, col + 1, '', td_cell_center)
                    sheet.write(row, col + 2, '', td_cell_center)
                    sheet.write(row, col + 3, formatLang(self.env, float_round(gross_profit, precision_digits=3)), td_cell_right_bold)
                    sheet.write(row, col + 4, float_round((gross_profit * 100) / net_revenue, precision_digits=3), td_cell_right_bold)
                    row += 1

                # profit before indirect expenses row
                if INCOME_EXPENSE_SEQUENCE[s] == 'indirect_expense':
                    if index == 0:
                        sheet.write(row, col, 'Profit Before Indirect Expenses', td_cell_left_bold)
                    sheet.write(row, col + 1, '', td_cell_center)
                    sheet.write(row, col + 2, '', td_cell_center)
                    sheet.write(row, col + 3, formatLang(self.env, float_round(profit_before_indirect_expense, precision_digits=3)), td_cell_right_bold)
                    sheet.write(row, col + 4, float_round((profit_before_indirect_expense * 100) / net_revenue, precision_digits=3), td_cell_right_bold)
                    row += 1

                # income, expense parent row
                if index == 0:
                    sheet.write(row, col, INCOME_EXPENSE_STRING[INCOME_EXPENSE_SEQUENCE[s]], td_cell_left_bold)
                sheet.write(row, col + 1, '', td_cell_center)
                sheet.write(row, col + 2, '', td_cell_center)
                sheet.write(row, col + 3, formatLang(self.env, float_round(amount, precision_digits=3)), td_cell_right_bold)
                sheet.write(row, col + 4, float_round((amount * 100) / net_revenue, precision_digits=3), td_cell_right_bold)

                # income, expense child row
                if INCOME_EXPENSE_SEQUENCE[s] != 'indirect_expense':
                    row += 1
                    for v in val:
                        net_realization = 0.0
                        if float(v['quantity']) > 0:
                            net_realization = float(v['amount'] / v['quantity'])
                        on_sale = float(v['amount'] * 100) / net_revenue

                        if index == 0:
                            sheet.write(row, col, '         ' + v['name'], td_cell_left)
                        sheet.write(row, col + 1, float_round(float(v['quantity']), precision_digits=3), td_cell_right)
                        sheet.write(row, col + 2, float_round(net_realization, precision_digits=3), td_cell_right)
                        sheet.write(row, col + 3, formatLang(self.env, float_round(float(v['amount']), precision_digits=3)), td_cell_right)
                        sheet.write(row, col + 4, float_round(on_sale, precision_digits=3), td_cell_right)
                        row += 1
                else:
                    row += 1
                    for seq in range(len(INDIRECT_EXPENSE_SEQUENCE)):
                        indirect_expense_val = val.get(INDIRECT_EXPENSE_SEQUENCE[seq])
                        total_expense_amount = float(sum(v['amount'] for v in indirect_expense_val))

                        # indirect expenses parent row
                        if index == 0:
                            sheet.write(row, col, '         ' + INDIRECT_EXPENSE_STRING[INDIRECT_EXPENSE_SEQUENCE[seq]], td_cell_left_bold)
                        sheet.write(row, col + 1, '', td_cell_center)
                        sheet.write(row, col + 2, '', td_cell_center)
                        sheet.write(row, col + 3, formatLang(self.env, float_round(total_expense_amount, precision_digits=3)), td_cell_right_bold)
                        sheet.write(row, col + 4, float_round((total_expense_amount * 100) / net_revenue, precision_digits=3), td_cell_right_bold)

                        row += 1
                        for exp_val in indirect_expense_val:
                            net_realization = 0.0
                            if float(exp_val['quantity']) > 0:
                                net_realization = float(v['amount'] / exp_val['quantity'])

                            on_sale = float(exp_val['amount'] * 100) / net_revenue

                            # indirect expense child row
                            if index == 0:
                                sheet.write(row, col, '                  ' + exp_val['name'], td_cell_left)
                            sheet.write(row, col + 1, float_round(float(exp_val['quantity']), precision_digits=3), td_cell_right)
                            sheet.write(row, col + 2, float_round(net_realization, precision_digits=3), td_cell_right)
                            sheet.write(row, col + 3, formatLang(self.env, float_round(float(exp_val['amount']), precision_digits=3)), td_cell_right)
                            sheet.write(row, col + 4, float_round(on_sale, precision_digits=3), td_cell_right)
                            row += 1

            # net profit row
            if index == 0:
                sheet.write(row, col, 'Net Profit', td_cell_left_bold)
            sheet.write(row, col + 1, '', td_cell_center)
            sheet.write(row, col + 2, '', td_cell_center)
            sheet.write(row, col + 3, formatLang(self.env, float_round(net_profit, precision_digits=3)), td_cell_right_bold)
            sheet.write(row, col + 4, float_round((net_profit * 100) / net_revenue, precision_digits=3), td_cell_right_bold)

            # set starting row for comparison
            row = 7
            col += 5


ProfitLossWithRealizationXLSX('report.samuda_account_reports.profit_loss_with_realization_xlsx', 'profit.loss.realization.wizard', parser=report_sxw.rml_parse)
