# -*- coding: utf-8 -*-
{
    'name': 'Event Management',
    'summary': """Core Module for Managing Different Types Of Events.""",
    'description': """Core Module for Managing Different Types Of Events""",
    'category': 'Event Management',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'version': '10.0.1.0.0',
    'depends': [
        'product',
        'account',
        'event',
    ],
    'data': [
        'security/event_security.xml',
        'security/ir.model.access.csv',
        'views/event_management_view.xml',
        'views/event_type_view.xml',
        'views/dashboard.xml',
        'data/event_management.xml',
    ],
    'demo': [
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': True,
}
