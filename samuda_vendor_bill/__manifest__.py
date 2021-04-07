# -*- coding: utf-8 -*-
{
    'name': 'Vendor Bill',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'version': '10.0.0.1',
    'depends': [
        'account_operating_unit',
        'l10n_bd_account_tax',
        'purchase',
    ],
    'data': [
        'views/account_invoice_view.xml'
    ],
    'summary': 'Vendor Bill',
    'installable': True,
    'application': False,
}
