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
        'event_management',
        'opa_utility',
    ],
    'data': [
        'views/event_reservation_templates.xml',
        'views/website_event_templates.xml',
        'data/email_template.xml',
        'report/access_barcode_views.xml',
    ],
    'installable': True,
    'application': True,
}
