# -*- coding: utf-8 -*-
{
    'name': "Stock Transfer Report",

    'summary': """
        Custom Stock Transfer Report""",

    'description': """
        By this report use can see details record of stock transfer.
        Also can get summary record.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': [
        'stock_operating_unit',
        'gbs_stock_product',
        'gbs_product_cost_price_history',
        'report_layout'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/stock_transfer_details_wizard.xml',
        'wizard/stock_transfer_summary_wizard.xml',
        'report/stock_transfer_details_report.xml',
        'report/stock_transfer_summary_report.xml',
    ]
}