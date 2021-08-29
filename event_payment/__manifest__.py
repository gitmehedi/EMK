# -*- coding: utf-8 -*-
{
    'name': 'Event Payments',
    'description': """
    All Kinds of Events Payment
    =======================
    1. Collect Event Fees Fees
    2. Card Replacement Fees
    3. All kinds of service changes including photocopy and other charges.
    """,
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Payments',
    'depends': [
        'account',
        'account_accountant',
        'membership_user',
        'emk_payment',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/ir_actions_server.xml',
        'data/default_data.xml',
        'views/menu_views.xml',
        'views/invoice_due.xml',
    ],
    'installable': True,
    'application': False,
}
