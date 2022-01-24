# -*- coding: utf-8 -*-
{
    'name': "Item Ledger Report",

    'summary': """""",

    'description': """
    """,

    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',

    'category': 'Warehouse Management',
    'version': '10.0.0.0.1',

    'depends': ['base', 'report_xlsx', 'report', 'stock_operating_unit', 'gbs_stock_product', 'stock_utility'],

    'data': [
        'wizards/item_ledger_report_wizard_view.xml',
        'reports/item_ledger_report_xlsx_view.xml',
    ],
}
