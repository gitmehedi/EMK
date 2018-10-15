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
        'report_layout',
        'mail_send',
        'event',
        'website_event',
        'event_user',
        'data_import',
        'event_session',
        'website_event_filter_selector'
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
        'views/event_close_view.xml',
        'views/res_partner_views.xml',
        'data/email_template.xml',
        'report/report_event_completion_form.xml',
        'report/event_monthly_report.xml',
        'wizard/wizard_event_session_view.xml',
        'wizard/wizard_monthly_event_view.xml',
    ],
    'installable': True,
    'application': True,
}
