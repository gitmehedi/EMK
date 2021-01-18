# -*- coding: utf-8 -*-
{
    'name': 'GBS Purchase Unit Price',
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
GBS Purchase Unit Price Update module
==============================

Key Features
------------
* Unit Price update only for local purchase at "Anticipatory Stock".
* Unit Price will not update for Foreign Purchase.""",
    'installable': True,
    'application': False,
}