# -*- coding: utf-8 -*-
{
    'name': "Vendor Security Deposit",
    'description': """
        Module is responsible for 'Vendor Security Deposit' functionality.This module included with-
        1. Vendor Security Deposit
        5. Vendor Security Return
        6. And related Accounting Treatment        

        """,
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'account_accountant'
    ],
    'data': [
        'data/data.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/account_config.xml',
        'views/vendor_security_return_view.xml',
        'views/vendor_security_deposit_view.xml',
        'views/inherit_account_invoice_view.xml'
        # 'views/menu.xml'

    ],
    'installable': True,
    'application': False,
}