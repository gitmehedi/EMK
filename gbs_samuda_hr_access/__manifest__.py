# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda HR Access",

    'summary': """
        This module will install for Samuda HR Access addons.""",

    'description': """
        This module will install for Samuda HR Access.  
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'gbs_hr_device_config',
        'base_user_role',
        'mass_editing',
        'google_drive',
    ],
    # always loaded
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/res_users.xml',
    ],
}