# -*- coding: utf-8 -*-
{
    'name': 'GBS Samuda Manufacturing Application with Access Rights',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Manufacturing',
    'version': '10.0.1.0.0',
    'summary': """
        This module will install for Samuda Manufacturing Access addons.""",

    'description': """
        This module will install for Samuda Manufacturing Access 
    """,

    # any module necessary for this one to work correctly
    'depends': [
        'mrp',
        'mrp_operating_unit',
        'mrp_operating_unit_extend',
        'mrp_extend',
        'mrp_accounting',
        'mrp_bom_extend',
        'mrp_bom_version',
        'mrp_bom_operating_unit',
        'mrp_account',
        'mrp_bom_product_user'
    ],

    # always loaded
    'data': [
        'security/mrp_gbs_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': True,
}