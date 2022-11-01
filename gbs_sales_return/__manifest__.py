# -*- coding: utf-8 -*-
{
    'name': "GBS Sales Return",

    'summary': """Sales Return customization """,

    'description': """
    """,

    'author': "Genweb2 Limited",

    'category': 'Uncategorized',
    'version': '10.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/inherited_stock_picking_view.xml',
    ],
}