# -*- coding: utf-8 -*-

{
    "name": "Sequence",
    "summary": "Operating unit that will be child of Operating Unit.",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        "base",
        "operating_unit",
        "mail",
        "mtbl_access",
    ],
    "data": [
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'wizard/sub_operating_unit_wizard_view.xml',
        'views/sub_operating_unit_view.xml',
    ],
    'installable': True,
    'application': True,
}
