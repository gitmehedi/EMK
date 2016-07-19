# -*- coding: utf-8 -*-

{
    'name': 'POS Receipt',
    'author':  'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Garments & Apparels',
    'data': [],
    'summary': 'POS receipt enhancement',
    'depends': ['point_of_sale'],
    'description': 'POS receipt enhancement',
    'category': 'Point Of Sale',
    'author': 'genweb2.com',
    'summary': 'POS module extension',
    'description': ' POS Module extension for POS receipt',
    'depends': [
                "point_of_sale"
                ],
  
    'qweb': [
        'static/src/xml/pos_ticket_enhanced_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}



