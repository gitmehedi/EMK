# -*- coding: utf-8 -*-

{
    'name': 'POS Promotion With Loyalty',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Garments & Apparels',
    'data': ['views/loyalty_rules_view.xml',
             'views/loyality_promotion_assets.xml',
             'views/assets.xml',
             'views/inherited_account_view.xml',
             'views/inherited_point_of_sale_view.xml',
             'views/promotion_rule_view.xml'
             ],
    'summary': 'POS promotion with loyalty integration',

    'description': 'POS promotion with loyalty integration',
    'category': 'Point Of Sale',
    'depends': [
        "point_of_sale"
    ],

    'qweb': [
        # 'static/src/xml/pos_enhanced_template.xml',
    ],
    'css': [
        'static/src/css/loyalty_promotion_custom.css',
    ],
    'js': [
        'static/src/js/pos_promotion_loyalty_custom.js',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
