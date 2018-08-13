# -*- coding: utf-8 -*-
{
    'name': 'Member Payment Process',
    'description': """ All kinds of payment of member which includes membership registration fees, card replacement fees, service,charge, photocopy fees""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Payments',
    'depends': [
        'member_signup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/payment_session_views.xml',
        'views/membership_fee_views.xml',
    ],
    'installable': True,
    'application': False,
}
