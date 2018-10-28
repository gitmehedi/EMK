# -*- coding: utf-8 -*-
{
    'name': 'Member Payment Process',
    'description': """ All kinds of payment of member which includes membership registration fees, card replacement fees, service,charge, photocopy fees""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Payments',
    'depends': [
        'account',
        'account_accountant',
        'membership_user',
        'member_signup',
        'member_card_replacement',
        'event_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/template.xml',
        'data/ir_actions_server.xml',
        'data/default_product.xml',
        'views/menu_views.xml',
        'views/payment_session_views.xml',
        'views/invoice_payment_views.xml',
        'views/invoice_due.xml',
        'views/service_payment_views.xml',
        'report/print_receipt_views.xml',
    ],
    'installable': True,
    'application': False,
}
