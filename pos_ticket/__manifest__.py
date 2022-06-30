# -*- encoding: utf-8 -*-

{
    "name": "PoS Ticket",
    "version": "10.0.0.1.0",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    "category": "Point Of Sale",
    "depends": ['base',
                'point_of_sale',
                'operating_unit',
                ],
    'data': [
        "views/pos_templates.xml",
        "views/operating_unit_view.xml",
    ],
    "qweb": [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
