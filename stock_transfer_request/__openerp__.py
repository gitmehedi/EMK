# -*- coding: utf-8 -*-

{
    'name': 'Stock Transfer Request',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Pebbles Module',
    'depends': ['base', 'stock', 'purchase', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/stock_transfer_receive_views.xml',
        'views/stock_transfer_request_views.xml',
    ],
    'summary': 'Test Summary for Stock Transfer Request',
    'category': 'Product',
    'summary': 'Stock Transfer Request',
    'description': 'Stock Transfer Request',
    'installable': True,
    'application': True,
}
