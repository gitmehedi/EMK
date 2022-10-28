# -*- coding: utf-8 -*-
{
    'name': 'Member Payments',
    'description': """ All kinds of payment of member which includes membership registration fees, card replacement fees, service,charge, photocopy fees""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Payments',
    'depends': [
        'account',
        'account_accountant',
        'emk_payment',
        'member_user',
        'membership_extension',
        'member_signup',
        'member_card_replacement',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/email_template.xml',
        'data/default_data.xml',
        'views/menu_views.xml',
        'views/payment_session_views.xml',
        'views/payment_operation_views.xml',
    ],
    'installable': True,
    'application': False,
}
