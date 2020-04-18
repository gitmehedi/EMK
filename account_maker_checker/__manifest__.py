# -*- coding: utf-8 -*-

{
    "name": "Account Maker & Checker",
    "summary": "Account Maker & Checker",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Accounting & Finance",
    "depends": [
        'base',
        'mail',
        'account'
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/account_account_wizard_view.xml',
        'views/inherit_account_account_view.xml'
    ],
    'installable': True,
    'application': True,
}