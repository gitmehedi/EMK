# -*- coding: utf-8 -*-
{
    'name': "Sales Return",
    'summary': """Return qty of Sale Order""",
    'author': "Genweb2",
    'website': "www.genweb2.com",
    'category': 'Stock',
    'version': '10.0.0.1',
    'depends': [
        'stock',
        'sale_stock'
    ],
    'data': [
        'wizard/stock_picking_return_views.xml',
        'wizard/inherited_stock_picking_return_view.xml',
        'wizard/success_wizard.xml'
    ]
}
