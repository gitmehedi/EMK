# -*- coding: utf-8 -*-
{
    'name': 'Sales Management',
    'description': """ All types of users whom are related to activities of Purchase Management""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Sales',
    'depends': [
        'sales_team',
        'sales_users',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_view.xml',
    ],
    'installable': True,
}

