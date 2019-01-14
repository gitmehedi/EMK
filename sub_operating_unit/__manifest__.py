# -*- coding: utf-8 -*-

{
    "name": "Sub Operating Unit",
    "summary": "Operating unit that will be child of Operating Unit.",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        "operating_unit",
    ],
    "data": [
        'security/ir.model.access.csv',
        'view/sub_operating_unit_view.xml',
    ],
    'installable': True,
    'application': True,
}
