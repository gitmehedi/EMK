# -*- coding: utf-8 -*-

{
    "name": "MTBL GL Master Data",
    "summary": "Master Data of mtbl",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        "base",
        'mail',
    ],
    "data": [
        'views/segment_view.xml',
        'views/servicing_channel.xml',
        'views/acquiring_channel.xml',
        'views/inherit_res_currency.xml',
    ],
    'installable': True,
    'application': True,
}
