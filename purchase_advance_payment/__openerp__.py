# -*- coding: utf-8 -*-
{
    'name': 'Purchase Advance Payment',
    'author': 'Genweb2 Limited',
    'website': 'https://genweb2.com',
    'category': 'Purchase',
    'data': [
        'wizard/purchase_make_invoice_advance_wizard.xml',
        'views/inherited_purchase_views.xml'
    ],
    'depends': [
        'base',
        'product',
        'point_of_sale',
        'stock',
        'purchase',
    ],
    'description': '''
''',
    'installable': True,
    'application': True,
    'auto_install': False,
}
