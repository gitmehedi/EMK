# -*- coding: utf-8 -*-

{
    "name": "Vendor/Customer",
    "summary": "",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        "base",
        'mail',
        'account',
        'base_vat_bd',
    ],
    "data": [
        # 'security/ir.model.access.csv',
        'wizard/res_partner_wizard_view.xml',
        # 'views/inherited_res_partner_view.xml',
        # 'views/inherit_res_partner.xml',
    ],
    'installable': True,
    'application': False,
}
