# -*- coding: utf-8 -*-
{
    'name': "Procure To Pay Access",

    'summary': """
        This module will install base required addons.""",

    'description': """
        This module will install base required addons.
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'commercial',
                'gbs_purchase_order',

    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu_items.xml',
    ],
}