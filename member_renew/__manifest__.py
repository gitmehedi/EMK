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
        'member_signup',
    ],
    'data': [
        'data/email_template.xml',
        'views/expiration_list_views.xml',
        'wizard/expiration_list_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
}
