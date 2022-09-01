# -*- coding: utf-8 -*-
{
    'name': 'EMK Payments',
    'description': """
    """,
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Payments',
    'depends': [
        'account',
        'account_accountant',
        'account_configuration',
    ],
    'data': [
        # 'data/sequence.xml',
        'data/email_template.xml',
        'data/ir_actions_server.xml',
        'data/default_data.xml',
        'views/menu_views.xml',
        'views/payment_session_views.xml',
        'views/invoice_payment_views.xml',
        'views/service_payment_views.xml',
        'views/service_types_views.xml',
        'views/invoice_due.xml',
        # 'report/print_receipt_views.xml',
    ],
    'installable': True,
    'application': False,
}
