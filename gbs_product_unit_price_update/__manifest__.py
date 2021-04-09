# -*- coding: utf-8 -*-
{
    'name': 'GBS Product Unit Price Update',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Manufacturing',
    'version': '10.0.1.0.0',
    'sequence': 14,
    'depends': [
        'stock_account',
    ],
    'data': [
    ],
    'summary': 'Override base module logic.',
    'description': """
GBS Product Unit Price Update module
==============================

Key Features
------------
* Product Unit Price Update for Local Purchase at "Anticipatory Stock".
* Product Unit Price will not Update for Foreign Purchase.
* Finish Goods Unit Price Update at Production""",
    'installable': True,
    'application': False,
}