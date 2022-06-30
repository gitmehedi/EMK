# -*- coding: utf-8 -*-
{
    'name': "Stock Inventory Gate Pass",
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Inventory',
    'summary': 'Stock Inventory Gate Pass',
    'description': 'Stock Inventory Gate Pass',
    'version': '10.0.1',
    'depends': [
        'mail_send',
        'base',
        'inventory_user',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/stock_inventory_gate_pass_view.xml',
    ],
}
