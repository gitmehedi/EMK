# -*- coding: utf-8 -*-
{
    'name': 'Point of Sale Permission',
    'description': """ All types of users whom are related to activities of Point of Sales""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Point of Sale',
    'depends': [
        'product',
        'account',
        'stock',
        'point_of_sale',
        'pos_users',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/point_of_sale_view.xml',
    ],
    'installable': True,
}

