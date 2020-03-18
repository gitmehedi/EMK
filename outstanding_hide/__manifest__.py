# -*- coding: utf-8 -*-
{
    'name': 'Hide Outstanding Payments and Outstanding Credits',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'version': '10.0.0.1',
    'depends': ['sale_order_type'],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'summary': 'When sale order type is LC, hide Outstanding Payments and Outstanding Credits from invoice form page.',
    'installable': True,
    'application': False,
}