# -*- coding: utf-8 -*-
{
    'name': "Product Standard Price Operating Unit",
    'summary': """ Operating Unit wise standard price of product """,
    'description': """ This module save the standard price of product and product price history operating unit wise""",
    'author': "Genweb2",
    'website': "www.genweb2.com",
    'category': 'Product',
    'version': '10.0.0.1',
    'depends': [
        'product',
        'stock_custom_summary_report',
        'stock_purchase_custom_report',
        'stock_transfer_report',
        'gbs_application_group'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/product_views.xml'
    ],
    'installable': True,
    'application': False,
}
