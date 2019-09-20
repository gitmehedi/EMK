# -*- coding: utf-8 -*-
{
    'name': "Stock Inventory Extend",

    'summary': """
        Extended Module For Stock Inventory.""",

    'description': """
        By this module stock inventory's customize features are added.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': ['stock_operating_unit'],

    'data': [
        # 'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/stock_inventory_views.xml',
    ],
}