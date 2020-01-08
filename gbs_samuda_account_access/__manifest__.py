# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Account Access",

    'summary': """
        This module will install for Samuda Account Access addons.""",

    'description': """
        This module will install for Samuda Account Access.  
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    
    'depends': [
        'gbs_accounting_installer',
    ],


    'data': [
        'views/inherited_account_view.xml',
        'views/inherited_account.xml',
        'security/ir_rule.xml',
    ],
}