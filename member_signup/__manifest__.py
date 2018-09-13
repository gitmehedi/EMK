# -*- coding: utf-8 -*-
{
    'name': 'Member Application',
    'description': """ Application for Membership""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'base',
        'mail',
        'website',
        'account',
        'account_accountant',
        'opa_utility',
        'membership',
        'membership_extension',
        'membership_user',
        'membership_withdrawal',
        'partner_firstname',
        'partner_second_lastname',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'data/member_signup_data.xml',
        'data/email_template.xml',
        'data/member_sequence.xml',
        'views/applicant_views.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_views.xml',
        'views/res_users_views.xml',
        'views/application_templates.xml',
        'views/member_config_views.xml',
        'views/pending_application_views.xml',
        'views/rfid_generation_views.xml',
        'views/member_config_settings_view.xml',
        'report/rfid_print_views.xml',
    ],
    'installable': True,
    'application': True,
}
