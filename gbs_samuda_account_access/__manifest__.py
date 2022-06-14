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
        'account',
        'gbs_accounting_installer',
        'account_fy_closing'
    ],


    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/lib_data.xml',
        'views/inherited_account_view.xml',
        'views/inherited_account.xml',
        'views/account_fiscalyear_close_view.xml',
        'views/inherited_account_invoice_view.xml',
        'security/ir_rule.xml',
    ],

    'qweb': [
        'static/src/xml/inherited_account_payment.xml'
    ],
}