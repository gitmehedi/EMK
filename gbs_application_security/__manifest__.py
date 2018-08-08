# -*- coding: utf-8 -*-
{
    'name': "GBS Application Security Group Package",

    'summary': """
        This module will install for Security.""",

    'description': """
        This module will install for Security.
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '0.1',
    'sequence': 500,
    # any module necessary for this one to work correctly
    'depends': [
        'gbs_application_group',
        'sale_operating_unit',
        'sale',
        'sale_order_type',
        'stock_operating_unit',
    ],

    # always loaded
    'data': [
        'security/ir_rule.xml',
        'views/stock_menu.xml',
    ],
}