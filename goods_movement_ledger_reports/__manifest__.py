# -*- coding: utf-8 -*-
{
    'name': "Goods Movement Ledger Reports",

    'summary': """""",

    'description': """
    """,

    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',

    'category': 'Manufacturing',
    'version': '10.0.0.0.1',

    'depends': ['base', 'report_xlsx', 'report', 'mrp_bom_product_user', 'stock_utility', 'item_transfer_process'],

    'data': [
        'wizards/variant_wise_report_wizard_view.xml',
        'wizards/variant_wise_inventory_report_wizard_view.xml',
        'wizards/multi_variant_report_wizard_view.xml',
        'wizards/multi_variant_inventory_report_wizard_view.xml',
        'reports/variant_wise_report_xlsx_view.xml',
        'reports/variant_wise_inventory_report_xlsx_view.xml',
        'reports/multi_variant_report_xlsx_view.xml',
        'reports/multi_variant_inventory_report_xlsx_view.xml'
    ],
}
