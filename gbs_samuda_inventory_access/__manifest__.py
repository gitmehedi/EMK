# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Inventory Access",

    'summary': """
        This module will install for Samuda Inventory Access addons.""",

    'description': """
        This module will install for Samuda Inventory Access.Its contain-
        --To hide unused menu
        --To override record rules
        --To override access rules  
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'purchase'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'views/product_views.xml',
        'views/menu_items.xml',
    ],
}