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
        'website_event',
        'event_user',
        'data_import',
        'event_session',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/ir_sequence.xml',
        'data/menu_view.xml',
        'views/dashboard.xml',
        'views/event_type_view.xml',
        'views/event_room_view.xml',
        'views/event_task_type.xml',
        'views/event_event_view.xml',
        'views/event_registration_view.xml',
        'views/event_task_list_view.xml',
        'views/event_session_view.xml',
        'views/res_partner_views.xml',
        'wizard/wizard_event_session_view.xml',
    ],
    'installable': True,
    'application': True,
}
