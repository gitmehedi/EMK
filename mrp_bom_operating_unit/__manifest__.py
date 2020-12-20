# -*- coding: utf-8 -*-

{
    'name': 'GBS MRP - BOM Operating Unit',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Manufacturing',
    'version': '10.0.1.0.0',
    'depends': [
        'mrp',
        'mrp_bom_version',
        'ir_sequence_operating_unit'
    ],
    'data': [
        'data/mrp_bom_sequence.xml',
        'views/mrp_bom_view.xml'
    ],
    'summary': 'BOM Operating Unit',
    'installable': True,
    'application': False,
}