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
        # 'event_barcode',
        'report_layout',
        'mail_send',
        'event',
        'website_event',
        'event_user',
        'website_event_filter_selector',
        'create_partner_user',
    ],
    'data': [
        'data/email_template.xml',
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'data/ir_sequence.xml',
        'data/data.xml',
        'wizard/wizard_monthly_event_view.xml',
        'wizard/data_import_wizard_view.xml',
        'views/menu_view.xml',
        'views/event_type_view.xml',
        'views/event_room_view.xml',
        'views/event_room_book_view.xml',
        'views/event_task_type_view.xml',
        'views/event_event_view.xml',
        'views/event_registration_view.xml',
        'views/event_task_list_view.xml',
        'views/event_close_view.xml',
        'views/res_partner_views.xml',
        'views/event_reservation_view.xml',
        'views/event_organization_type_view.xml',
        'report/report_event_completion_form.xml',
        'report/monthly_event_report_view.xml',
    ],
    'installable': True,
    'application': True,
}
