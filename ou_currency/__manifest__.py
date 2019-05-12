# -*- coding: utf-8 -*-
{
    "name": "Operating Unit Currency",
    "summary": "Added Currency For Operating Unit",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        "operating_unit",
        "mtbl_access",
    ],
    "data": [
        # 'security/ir.model.access.csv',
        'views/inherit_operating_unit.xml',

    ],
    'installable': True,
    'application': False,
}
