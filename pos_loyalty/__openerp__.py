# -*- coding: utf-8 -*-

{
    'name': 'POS Loyalty',
    'author':  'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Garments & Apparels',
    'data': ['views/loyalty_rules_view.xml',
            'views/pos_loyality_template.xml',
            'views/assets.xml',
            'views/inherited_account_view.xml',
            'views/inherited_point_of_sale_view.xml',
             ],
    'summary': 'Test Summary for POS Loyalty',
    'depends': ['point_of_sale'],
    'description': 'Test Description',
    'category': 'Point Of Sale',
    'author': 'genweb2.com',
    'summary': 'POS module extension',
    'description': ' POS Module extension for point calculation ',
    'depends': [
                "point_of_sale"
                ],
  
    'qweb': [
        'static/src/xml/pos_enhanced_template.xml',
    ],
    'css': [ 
           'static/src/css/pos_loyalty_custom.css',   
           ],
    'js': [ 
           'static/src/js/pos_loyalty_custom.js',   
           ],
    'installable': True,
    'application': True,
    'auto_install': False,
}



