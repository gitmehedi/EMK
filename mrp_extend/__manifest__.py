# -*- coding: utf-8 -*-
{
    'name': 'GBS MRP extend',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Manufacturing',
    'version': '10.0.1.0.0',
    'depends': [
        'mrp',
        'mrp_bom_extend'
    ],
    'data': [
        'views/inherited_mrp_production_views.xml',
        'views/inherited_product_views.xml'
    ],
    'summary': 'Adding standard qty field and modified existing features',
    'installable': True,
    'application': False,
}