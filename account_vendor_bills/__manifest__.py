# -*- coding: utf-8 -*-

{
    "name": "Account Vendor Bills",
    "summary": "Account Vendor Bills",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        'account',
        'analytic',
        'account_parent',
        'account_operating_unit',
        'l10n_bd_account_tax',
    ],
    "data": [
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'application': True,
}
