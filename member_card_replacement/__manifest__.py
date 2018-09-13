{
    'name': 'Membership Card Replacement',
    'description': """ Replacement of Membership Card""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'opa_utility',
        'member_renew',
        'membership_user',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/sequence.xml',
        'data/default_product.xml',
        'views/card_replacement_views.xml',
    ],
    'installable': True,
    'application': False,
}
# -*- coding: utf-8 -*-
