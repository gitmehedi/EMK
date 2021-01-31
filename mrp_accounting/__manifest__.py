# -*- coding: utf-8 -*-
{
    'name': 'GBS MRP Accounting',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Manufacturing',
    'version': '10.0.1.0.0',
    'sequence': 14,
    'depends': [
        'mrp',
        'account',
        'delivery_order',
    ],
    'data': [
        'views/inherited_mrp_config_settings_views.xml',
        'views/product_view.xml',
        'views/inherit_mrp_production_view.xml'
    ],
    'summary': 'MRP Accounting',
    'installable': True,
    'application': False,
}