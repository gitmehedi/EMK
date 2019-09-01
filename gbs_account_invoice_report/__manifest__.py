# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'GBS Account Invoice Report',
    'version' : '10.0.0.1',
    'summary': 'Custom Report of Account Invoice',
    'sequence': 300,
    'description': """
Invoicing & Payments
====================
The specific and easy-to-view report of account invoice.This is custom analytic report 
    """,
    'category': 'Accounting',
    'website': 'www.genweb2.com',
    'author': 'Genweb2 Limited',
    'depends' : ['account'],
    'data': [
        'report/account_invoice_report_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
