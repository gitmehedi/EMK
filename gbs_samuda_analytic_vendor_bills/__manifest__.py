# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Analytic Account with Vendor Bills",

    'summary': """
        Analytic Account Integration for foreign purchase with vendor bills""",

    'description': """
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Accounting',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'account'],

    # always loaded
    'data': [
        'views/inherited_account_account_view.xml',
        'views/inherited_account_invoice_view.xml',

    ],

}
