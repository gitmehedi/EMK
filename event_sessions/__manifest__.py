# -*- coding: utf-8 -*-

{
    'name': 'Event Sessions',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Event Management',
    'summary': 'Sessions in events',
    'depends': [
        'event',
        'event_mail',
        'event_management',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/event_session_security.xml',
        'views/event_session_view.xml',
        'views/event_session_attend_view.xml',
        'views/event_view.xml',
        'wizards/wizard_event_session_view.xml',
        # 'reports/report_event_registration_view.xml',
    ],
    'installable': True,
    'application': True,
}
