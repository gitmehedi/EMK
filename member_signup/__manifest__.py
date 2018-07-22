# -*- coding: utf-8 -*-
{
    'name': 'Membership SignUp',
    'description': """ Membership signup """,
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'base',
        'mail',
        'website',
        'membership',
        'membership_extension',
        'membership_withdrawal',
    ],
    'data': [
        'data/member_signup_data.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/res_partner_views.xml',
        'views/res_config_views.xml',
        'views/res_users_views.xml',
        'views/member_application_templates.xml',
        'views/member_config_views.xml',
        'views/member_application_views.xml',
    ],
    'bootstrap': True,
}
