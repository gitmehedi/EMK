# -*- coding: utf-8 -*-
{
    'name': "GBS Customer Invoice Modification",

    'summary': """""",

    'description': """
    
* Only Customer Invoice Editor Group can edit Customer Invoices.

* Customer Invoice default create option has been omitted.

* Manual Invoice Creation option for Ship Invoices
    
    """,

    'author': "Genweb2 Limited",

    'category': 'Uncategorized',
    'version': '10.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/inherited_account_invoice_view.xml',
        'views/manual_invoice_view.xml'
    ],
}