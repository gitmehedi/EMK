# -*- coding: utf-8 -*-
{
    'name': 'Sales Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales Reports',
    'version': '10.0.0.1',
    'depends': ['account'],
    'data': [
        'wizard/customer_aging_statement_wizard.xml',
        'reports/customer_aging_statement.xml',
    ],

    'summary': 'Sales Reports Information',
    'installable': True,
    'application': True,
}