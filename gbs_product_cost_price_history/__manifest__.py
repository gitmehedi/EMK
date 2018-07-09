# -*- coding: utf-8 -*-
{
    'name': "Product Cost Price History",
    'summary': """
        History Of Product Variant Cost Price History
        """,
    'description': """
        This module save the history list of all product purchased price in variant wise.
    """,
    'author': "Genweb2",
    'website': "www.genweb2.com",
    'category': 'Warehouse',
    'version': '10.0.1',
    'depends': [
        'purchase',
        'stock_move_backdating',
        'stock_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_cost_price_history_views.xml',
    ],
    'installable': True,
    'application': True,
}
