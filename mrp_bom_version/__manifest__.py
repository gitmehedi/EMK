# -*- coding: utf-8 -*-

{
    'name': 'GBS MRP - BOM version',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Manufacturing',
    'version': '10.0.1.0.0',
    'depends': [
        'mrp'
    ],
    'data': [
        'data/mrp_bom_sequence.xml',
        # 'wizard/mrp_bom_wizard_view.xml',
        'views/mrp_bom_view.xml'
    ],
    'summary': 'BOM Versioning',
    'installable': True,
    'application': False,
}