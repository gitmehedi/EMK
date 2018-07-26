# -*- coding: utf-8 -*-
{
    'name': "GBS Application Generic Group Package",

    'summary': """
        This module will install for GBS Application Generic Group.""",

    'description': """
        This module will install for GBS Application Generic Group.
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'gbs_res_users',
        'operating_unit',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir_rule.xml',
    ],
}