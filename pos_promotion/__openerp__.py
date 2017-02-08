# -*- coding: utf-8 -*-

{
    'name': 'POS Promotion',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Point Of Sale',
    'data': [
        'views/promotion_rule_view.xml',
        'views/pos_promotion_assets.xml',
        'views/inherited_point_of_sale_view.xml'
    ],
    'summary': 'POS promotion for applying prmotion on product',
    'qweb': [
        'static/src/xml/pos_promotion_template.xml'
    ],
    'depends': ['point_of_sale'],
    'description': """POS promotion for applying prmotion on product""",
    'installable': True,
    'application': True,
    'auto_install': False,
}
