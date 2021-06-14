from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.misc import formatLang
from odoo.tools import float_compare, float_round

IE_ORDER = {
    0: 'revenue',
    1: 'indirect_income',
    2: 'raw_material',
    3: 'packing_material',
    4: 'utility_bill',
    5: 'direct_material',
    6: 'labour_charge',
    7: 'prime_cost',
    8: 'factory_overhead',
    9: 'amortization',
    10: 'depreciation',
    11: 'manufacturing_cost',
    12: 'cogs',
    13: 'administrative',
    14: 'finance',
    15: 'marketing',
    16: 'distribution',
    17: 'total_cost',
    18: 'profit_loss'
}
IE_NAME = {
    'revenue': 'Revenue',
    'indirect_income': 'Indirect Incomes',
    'raw_material': 'Raw Material Consumed',
    'packing_material': 'Packing Material Consumed',
    'utility_bill': 'Utility Bill Consumed',
    'direct_material': 'Direct Material Consumed',
    'labour_charge': 'Labour Charge',
    'prime_cost': 'Prime Cost',
    'factory_overhead': 'General Factory Overhead',
    'amortization': 'Amortization',
    'depreciation': 'Depreciation',
    'manufacturing_cost': 'Manufacturing Cost',
    'cogs': 'Cost Of Goods Sold',
    'administrative': 'Administrative Expenses',
    'finance': 'Finance Expenses',
    'marketing': 'Marketing Expenses',
    'distribution': 'Distribution Expenses',
    'total_cost': 'Total Cost',
    'profit_loss': 'Profit/Loss'
}
ACCOUNT_TAG = {
    'utility_bill': 'CS-Utility Bill',
    'labour_charge': 'CS-Labour Charge',
    'depreciation': 'CS-Depreciation',
    'amortization': 'CS-Amortization',
    'factory_overhead': 'CS-Factory Exp',
    'indirect_income': 'CS-Indirect Inc',
    'administrative': 'CS-Admin Exp',
    'finance': 'CS-Finance Exp',
    'marketing': 'CS-Marketing Exp',
    'distribution': 'CS-Dist Exp'
}

GROUP_TOTAL_NAMES = ['direct_material', 'prime_cost', 'manufacturing_cost', 'total_cost', 'profit_loss']
INCOME_USER_TYPE_ID = 14
RM_CATEGORY_ID = 69
PM_CATEGORY_ID = 70


class CostSheetXLSX(ReportXlsx):

    def _get_query_where_clause(self, obj, date_from, date_to):
        where_clause = " WHERE aml.date BETWEEN '%s' AND '%s'" % (date_from, date_to)
        where_clause += " AND aml.cost_center_id=%s AND aml.company_id=%s" % (obj.cost_center_id.id, self.env.user.company_id.id)
        if not obj.all_entries:
            where_clause += " AND mv.state='posted'"
        if obj.operating_unit_id:
            where_clause += " AND aml.operating_unit_id=%s" % obj.operating_unit_id.id

        return where_clause

    def _get_revenue(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        account_ids = self.env['account.account'].search([('user_type_id', '=', INCOME_USER_TYPE_ID)]).ids
        if account_ids:
            param = (tuple(account_ids),)
            where_clause += " AND aml.account_id IN %s" % param

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name,
                        COALESCE(SUM(aml.quantity), 0) AS quantity,
                        -(SUM(aml.debit)-SUM(aml.credit)) AS amount
                    FROM
                        account_move_line aml
                        JOIN account_move mv ON mv.id=aml.move_id
                        JOIN account_cost_center acc ON acc.id=aml.cost_center_id
                    """ + where_clause + """ GROUP BY aml.cost_center_id,acc.name 
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
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['indirect_income'], self.env.user.company_id.id)

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

    def _get_raw_material(self, obj, date_from, date_to):
        where_clause = """ WHERE mrp.state='done' AND m.state='done' AND m.company_id=%s AND pt.cost_center_id=%s
        AND DATE(m.date + interval '6h') BETWEEN DATE('%s')+time '00:00' AND DATE('%s')+time '23:59:59'""" % (
        self.env.user.company_id.id, obj.cost_center_id.id, date_from, date_to)

        if obj.operating_unit_id:
            where_clause += " AND mrp.operating_unit_id=%s" % obj.operating_unit_id.id

        sql = """SELECT
                        SUM(m.quantity_done_store) AS quantity
                    FROM
                        stock_move m
                        JOIN mrp_production mrp ON mrp.id=m.production_id
                        JOIN product_product pp ON pp.id=m.product_id
                        JOIN product_template pt ON pt.id=pp.product_tmpl_id
                        JOIN account_cost_center acc ON acc.id=pt.cost_center_id
                    """ + where_clause

        production_qty = 0
        self.env.cr.execute(sql)
        for row in self.env.cr.dictfetchall():
            production_qty += row['quantity'] or 0.0

        sql_str = """SELECT
                        m.product_id,
                        t.name,
                        0.0 AS quantity,
                        SUM(m.quantity_done_store * m.price_unit) AS amount
                    FROM
                        stock_move m
                        JOIN product_product p ON p.id=m.product_id
                        JOIN product_template t ON t.id=p.product_tmpl_id
                        JOIN product_category c ON c.id=t.categ_id
                        JOIN mrp_production mrp ON mrp.id=m.raw_material_production_id
                        JOIN product_product pp ON pp.id=mrp.product_id
                        JOIN product_template pt ON pt.id=pp.product_tmpl_id
                        JOIN account_cost_center acc ON acc.id=pt.cost_center_id
                    """ + where_clause + """ AND t.categ_id!=%s GROUP BY m.product_id,t.name ORDER BY m.product_id,t.name""" % PM_CATEGORY_ID

        item_list = []
        Product = self.env['product.product']

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            product = Product.search([('id', '=', row['product_id']), ('active', '=', True)])
            row['name'] = product[0].display_name
            row['quantity'] = production_qty
            item_list.append(row)

        return item_list

    def _get_packing_material(self, obj, date_from, date_to):
        where_clause = """ WHERE mrp.state='done' AND m.state='done' AND m.company_id=%s AND pt.cost_center_id=%s
                AND DATE(m.date + interval '6h') BETWEEN DATE('%s')+time '00:00' AND DATE('%s')+time '23:59:59'""" % (
            self.env.user.company_id.id, obj.cost_center_id.id, date_from, date_to)

        if obj.operating_unit_id:
            where_clause += " AND mrp.operating_unit_id=%s" % obj.operating_unit_id.id

        sql = """SELECT
                    SUM(m.quantity_done_store) AS quantity
                FROM
                    stock_move m
                    JOIN mrp_production mrp ON mrp.id=m.production_id
                    JOIN product_product pp ON pp.id=m.product_id
                    JOIN product_template pt ON pt.id=pp.product_tmpl_id
                    JOIN account_cost_center acc ON acc.id=pt.cost_center_id
                """ + where_clause

        production_qty = 0
        self.env.cr.execute(sql)
        for row in self.env.cr.dictfetchall():
            production_qty += row['quantity'] or 0.0

        sql_str = """SELECT
                        m.product_id,
                        t.name,
                        0.0 AS quantity,
                        SUM(m.quantity_done_store * m.price_unit) AS amount
                    FROM
                        stock_move m
                        JOIN product_product p ON p.id=m.product_id
                        JOIN product_template t ON t.id=p.product_tmpl_id
                        JOIN product_category c ON c.id=t.categ_id
                        JOIN mrp_production mrp ON mrp.id=m.raw_material_production_id
                        JOIN product_product pp ON pp.id=mrp.product_id
                        JOIN product_template pt ON pt.id=pp.product_tmpl_id
                        JOIN account_cost_center acc ON acc.id=pt.cost_center_id
                    """ + where_clause + """ AND t.categ_id=%s GROUP BY m.product_id,t.name ORDER BY m.product_id,t.name""" % PM_CATEGORY_ID

        item_list = []
        Product = self.env['product.product']

        self.env.cr.execute(sql_str)
        for row in self.env.cr.dictfetchall():
            product = Product.search([('id', '=', row['product_id']), ('active', '=', True)])
            row['name'] = product[0].display_name
            row['quantity'] = production_qty
            item_list.append(row)

        return item_list

    def _get_utility_bill(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                    aa.id 
                                                FROM 
                                                    account_account aa
                                                    JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                    JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                WHERE
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['utility_bill'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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

    def _get_labour_charge(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN (SELECT 
                                                    aa.id 
                                                FROM 
                                                    account_account aa
                                                    JOIN account_account_account_tag aaat ON aaat.account_account_id=aa.id
                                                    JOIN account_account_tag aat ON aat.id=aaat.account_account_tag_id
                                                WHERE
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['labour_charge'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['factory_overhead'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        COALESCE(SUM(aml.quantity), 0) AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['amortization'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        COALESCE(SUM(aml.quantity), 0) AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['depreciation'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        COALESCE(SUM(aml.quantity), 0) AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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

    def _get_cogs(self, obj, date_from, date_to):
        item_list = []

        where_clause = self._get_query_where_clause(obj, date_from, date_to)
        where_clause += """ AND aml.account_id IN ((SELECT raw_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id=%s) UNION
                                                    (SELECT packing_cogs_account_id AS account_id FROM product_template WHERE sale_ok=true AND active=true AND cost_center_id=%s))""" % (obj.cost_center_id.id, obj.cost_center_id.id)

        sql_str = """SELECT
                        aml.cost_center_id,
                        acc.name,
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
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['administrative'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['finance'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['marketing'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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
                                                    aat.name='%s' AND aa.company_id=%s)""" % (ACCOUNT_TAG['distribution'], self.env.user.company_id.id)

        sql_str = """SELECT
                        aml.account_id,
                        aa.name,
                        0 AS quantity,
                        (SUM(aml.debit)-SUM(aml.credit)) AS amount
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

    def finalize_comparison_table_data(self, data_list):
        for n in range(len(IE_ORDER)):

            if IE_ORDER[n] in GROUP_TOTAL_NAMES:
                continue

            attr_name = 'account_id'
            model_name = 'account.account'
            if IE_ORDER[n] in ['raw_material', 'packing_material']:
                attr_name = 'product_id'
                model_name = 'product.product'

            if IE_ORDER[n] in ['revenue', 'cogs']:
                attr_name = 'cost_center_id'
                model_name = 'account.cost.center'

            unique_ids = set()
            for item in data_list:
                id_list = map(lambda x: x[attr_name], item[IE_ORDER[n]])
                unique_ids.update(set(id_list))

            for item in data_list:
                temp_list = []
                id_list = map(lambda x: x[attr_name], item[IE_ORDER[n]])
                diff_ids = unique_ids.difference(set(id_list))
                for d_id in list(diff_ids):
                    if model_name == 'product.product':
                        name = self.env[model_name].search([('id', '=', d_id)])[0].display_name
                    else:
                        name = self.env[model_name].search([('id', '=', d_id)])[0].name
                    temp_list.append({attr_name: d_id, 'name': name, 'quantity': 0, 'amount': 0})

                if temp_list:
                    temp_list.extend(item[IE_ORDER[n]])
                    item[IE_ORDER[n]] = sorted(temp_list, key=lambda l: (l[attr_name], l['name']))

        return data_list

    @staticmethod
    def calc_group_total(item_dict):
        income = direct_material = labour_charge = manufacturing_cost = total_cost = 0.0

        for key, item_list in item_dict.items():
            if key == 'labour_charge':
                labour_charge += float(sum(item['amount'] for item in item_list)) or 0.0
            elif key in ['revenue', 'indirect_income']:
                income += float(sum(item['amount'] for item in item_list)) or 0.0
            elif key in ['raw_material', 'packing_material', 'utility_bill']:
                direct_material += float(sum(item['amount'] for item in item_list)) or 0.0
            elif key in ['factory_overhead', 'amortization', 'depreciation']:
                manufacturing_cost += float(sum(item['amount'] for item in item_list)) or 0.0
            else:
                total_cost += float(sum(item['amount'] for item in item_list)) or 0.0

        prime_cost = direct_material + labour_charge
        manufacturing_cost += prime_cost
        profit_loss = income - total_cost

        return {'direct_material': direct_material,
                'prime_cost': prime_cost,
                'manufacturing_cost': manufacturing_cost,
                'total_cost': total_cost,
                'profit_loss': profit_loss}

    @staticmethod
    def calc_rate(amount, sale_qty, production_qty, name):
        rate = 0.0
        if name in ['revenue', 'indirect_income', 'administrative', 'finance', 'marketing', 'distribution', 'total_cost', 'profit_loss']:
            if sale_qty > 0:
                rate = amount / sale_qty
        else:
            if production_qty > 0:
                rate = amount / production_qty

        return rate

    @staticmethod
    def calc_sales_qty(item_list):
        return float(sum(item['quantity'] for item in item_list)) or 0.0

    @staticmethod
    def get_production_qty(item_list):
        qty = 0.0
        if item_list:
            qty = item_list[0]['quantity']

        return qty

    def generate_xlsx_report(self, workbook, data, obj):
        report_data_list = []
        comparison_table = obj.get_periods()
        for tbl in comparison_table:
            item_dict = dict()
            item_dict['revenue'] = self._get_revenue(obj, tbl[0], tbl[1])
            item_dict['indirect_income'] = self._get_indirect_income(obj, tbl[0], tbl[1])
            item_dict['raw_material'] = self._get_raw_material(obj, tbl[0], tbl[1])
            item_dict['packing_material'] = self._get_packing_material(obj, tbl[0], tbl[1])
            item_dict['utility_bill'] = self._get_utility_bill(obj, tbl[0], tbl[1])
            item_dict['labour_charge'] = self._get_labour_charge(obj, tbl[0], tbl[1])
            item_dict['factory_overhead'] = self._get_factory_overhead(obj, tbl[0], tbl[1])
            item_dict['amortization'] = self._get_amortization(obj, tbl[0], tbl[1])
            item_dict['depreciation'] = self._get_depreciation(obj, tbl[0], tbl[1])
            item_dict['cogs'] = self._get_cogs(obj, tbl[0], tbl[1])
            item_dict['administrative'] = self._get_administrative_expense(obj, tbl[0], tbl[1])
            item_dict['finance'] = self._get_finance_expense(obj, tbl[0], tbl[1])
            item_dict['marketing'] = self._get_marketing_expense(obj, tbl[0], tbl[1])
            item_dict['distribution'] = self._get_distribution_expense(obj, tbl[0], tbl[1])

            report_data_list.append(item_dict)

        if obj.comparison:
            report_data_list = self.finalize_comparison_table_data(report_data_list)

        # FORMAT
        bold = workbook.add_format({'bold': True, 'size': 10})
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
        sheet = workbook.add_worksheet('Cost Sheet')

        # SET CELL WIDTH
        col = 0
        for index, _ in enumerate(comparison_table):
            if index == 0:
                sheet.set_column(col, col, 50)
            sheet.set_column(col + 1, col + 1, 22)
            sheet.set_column(col + 2, col + 2, 18)
            col += 3

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, 2, self.env.user.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, 2, self.env.user.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, 2, self.env.user.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, 2, self.env.user.company_id.city + '-' + self.env.user.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, 2, "Cost Sheet of " + obj.cost_center_id.name, name_format)

        sheet.write(6, 0, "Cost Center: " + obj.cost_center_id.name, bold)

        if obj.operating_unit_id:
            sheet.merge_range(6, 1, 6, 2, "Operating Unit: " + obj.operating_unit_id.name, bold)
        else:
            sheet.merge_range(6, 1, 6, 2, "Operating Unit: All", bold)

        # TABLE HEADER
        row, col = 8, 0
        for index, value in enumerate(comparison_table):
            if index == 0:
                sheet.write(row, col, '', th_cell_center)
            sheet.merge_range(row, col + 1, row, col + 2, obj.get_full_date_names(value[1], value[0]), th_cell_center)
            col += 3

        row += 3
        col = 0
        for index, _ in enumerate(comparison_table):
            if index == 0:
                sheet.write(row, col, 'Particulars', th_cell_center)
            sheet.write(row, col + 1, 'Cost', th_cell_center)
            sheet.write(row, col + 2, 'Cost per MT', th_cell_center)
            col += 3

        # TABLE BODY
        row += 1
        col = 0
        for index, value in enumerate(report_data_list):

            production_qty = self.get_production_qty(value['raw_material']) or self.get_production_qty(value['packing_material'])
            sale_qty = self.calc_sales_qty(value['revenue'])
            group_total_dict = self.calc_group_total(value)

            # SALES AND PRODUCTION QUANTITY ROW
            if index == 0:
                sheet.write(row-3, col, '', th_cell_center)
                sheet.write(row-2, col, '', th_cell_center)
            sheet.merge_range(row-3, col + 1, row-3, col + 2, 'Sales Quantity: ' + str(sale_qty) + ' MT', th_cell_center)
            sheet.merge_range(row-2, col + 1, row-2, col + 2, 'Production Quantity: ' + str(production_qty) + ' MT', th_cell_center)
            # SALES AND PRODUCTION QUANTITY ROW

            for n in range(len(IE_ORDER)):
                # GROUP TOTAL ROW
                grp_amount = group_total_dict.get(IE_ORDER[n], 0)
                grp_rate = self.calc_rate(grp_amount, sale_qty, production_qty, IE_ORDER[n])

                if IE_ORDER[n] in GROUP_TOTAL_NAMES:
                    if index == 0:
                        sheet.write(row, col, IE_NAME[IE_ORDER[n]], td_cell_left_bold)
                    sheet.write(row, col + 1, float_round(grp_amount, precision_digits=2), td_cell_right_bold)
                    sheet.write(row, col + 2, float_round(grp_rate, precision_digits=2), td_cell_right_bold)
                    row += 1
                    continue
                # END GROUP TOTAL ROW

                item_list = value.get(IE_ORDER[n])

                # PARENT ROW
                pr_amount = float(sum(item['amount'] for item in item_list)) or 0.0
                pr_rate = self.calc_rate(pr_amount, sale_qty, production_qty, IE_ORDER[n])

                if index == 0:
                    sheet.write(row, col, IE_NAME[IE_ORDER[n]], td_cell_left_bold)
                sheet.write(row, col + 1, float_round(pr_amount, precision_digits=2), td_cell_right_bold)
                sheet.write(row, col + 2, float_round(pr_rate, precision_digits=2), td_cell_right_bold)
                row += 1
                # END PARENT ROW

                # CHILD ROWS
                for item in item_list:
                    ch_rate = self.calc_rate(float(item['amount']), sale_qty, production_qty, IE_ORDER[n])

                    if index == 0:
                        sheet.write(row, col, '         ' + item['name'], td_cell_left)
                    sheet.write(row, col + 1, float_round(float(item['amount']), precision_digits=2), td_cell_right)
                    sheet.write(row, col + 2, float_round(ch_rate, precision_digits=2), td_cell_right)
                    row += 1
                # END CHILD ROWS

            # set starting row for comparison
            row = 12
            col += 3


CostSheetXLSX('report.samuda_account_reports.cost_sheet_xlsx', 'cost.sheet.wizard', parser=report_sxw.rml_parse)
