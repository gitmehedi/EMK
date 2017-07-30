# -*- coding: utf-8 -*-
{
    'name': "Sales Group Package",

    'summary': """
        This module will install base required addons.""",

    'description': """
        This module will install base required addons.
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
    ],

    # always loaded
    'data': [
        'security/security.xml',
    ],
}