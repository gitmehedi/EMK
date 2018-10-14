# -*- coding: utf-8 -*-

{
    'name': 'Event Registration',
    'summary': 'Schedule, Promote and Sell Events',
    'category': 'Event Management',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'version': '10.0.1.0.0',
    'sequence': 135,
    'description': """
        Event Registration
        """,
    'depends': [
        'website',
        'website_event',
        'assets',
        'event_management',
    ],
    'data': [
        'views/website_event_templates.xml',
    ],
    'installable': True,
    'application': True,
}
