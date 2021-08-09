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
        'document',
        'account',
        'hr',
        'account_accountant',
        'opa_utility',
        'membership',
        'membership_extension',
        'membership_user',
        'membership_withdrawal',
        'partner_fullname',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'data/member_signup_data.xml',
        'data/email_template.xml',
        'data/member_sequence.xml',
        'views/menu_views.xml',
        'wizard/set_membership_views.xml',
        'views/application_views.xml',
        'views/applicant_profile_views.xml',
        'views/member_views.xml',
        'views/membership_types_views.xml',
        'views/res_config_views.xml',
        'views/membership_withdrawl_reason_views.xml',
        'views/membership_categories_views.xml',
        'views/res_users_views.xml',
        'views/application_templates.xml',
        'views/member_config_views.xml',
        'views/rfid_generation_views.xml',
        'views/member_config_settings_view.xml',
        'views/service_types_views.xml',
        'report/rfid_print_views.xml',
    ],
    'installable': True,
    'application': True,
}
