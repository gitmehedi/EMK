# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Sales Access",

    'summary': """
        This module will install for Samuda Sales Access addons.""",

    'description': """
        This module will install for Samuda Sales Access.  
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'product_harmonized_system',
        'sales_team',
        'gbs_application_group',
        'stock',
    ],


    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],
}