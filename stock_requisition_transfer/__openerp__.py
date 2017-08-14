# -*- coding: utf-8 -*-

{
    'name': 'Stock Requisition Transfer',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Pebbles Module',
    'depends': ['base', 'stock', 'purchase', 'product', 'pebbles_transfer_user'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/menu.xml',
        'views/stock_requisition_transfer_views.xml',
        'views/stock_requisition_approval_views.xml',
        'views/stock_requisition_request_views.xml',
        'reports/stock_requisition_views.xml',
        'reports/stock_requisition_menu.xml',
    ],
    "qweb": [
        'static/src/xml/template.xml',
    ],
    'summary': 'Test Summary for Stock Transfer Request',
    'category': 'Product',
    'summary': 'Stock Requisition Transfer',
    'description': 'Stock Requisition Transfer',
    'installable': True,
    'application': True,
}
