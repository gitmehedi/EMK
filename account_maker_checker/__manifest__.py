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
        'account',
        'account_mtbl',
        'l10n_bd_account_tax'
    ],
    "data": [
        # 'wizard/account_account_wizard_view.xml',
        # 'views/inherit_account_account_view.xml',
        'wizard/account_tax_wizard_view.xml',
        'views/inherit_account_tax.xml'
    ],
    'installable': True,
    'application': True,
}
