# -*- coding: utf-8 -*-

{
    'name': 'POS Invoice Format',
    'author':  'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Point of Sale',
    'summary': 'This is custom pos invoice format to print A4 size bill.',
    'depends': ['point_of_sale'],
    'description': 'This is custom pos invoice format to print A4 size bill.',
    'category': 'Point Of Sale',
    'author': 'genweb2.com',
    'summary': 'POS module extension',
    'description': ' POS Module extension for custom pos invoice format to print A4 size bill. ',
    'depends': [
                "point_of_sale"
                ],
    'data': [
            'views/pos_custom_invoice_format_assets.xml',
             ],
    'qweb': [
        'static/src/xml/pos_custom_invoice_format_template.xml',
    ],
    'css': [ 
           'static/src/css/pos_custom_invoice_format.css',   
           ],
    'installable': True,
    'application': True,
    'auto_install': False,
}



