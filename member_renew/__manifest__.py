# -*- coding: utf-8 -*-
{
    'name': 'Member Renew Module',
    'description': """ Module is responsible for Membership Renew""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'mail',
        'account',
        'membership_user',
        'member_signup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/email_template.xml',
        'data/ir_actions_server.xml',
        'views/expiration_list_views.xml',
        'views/renew_request_views.xml',
        'views/invoice_due.xml',
        'wizard/expiration_list_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
}
