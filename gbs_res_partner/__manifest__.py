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
        # 'base_vat_bd',
        'gbs_bd_division',
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/res_partner_wizard_view.xml',
        'wizard/vendor_designation_wizard_view.xml',
        'wizard/entity_service_wizard_view.xml',
        'views/vendor_designation_view.xml',
        'views/entity_service_view.xml',
        'views/inherited_res_partner_view2.xml',
        'views/inherited_res_partner_view.xml',
        'views/account_config.xml',
],
    'installable': True,
    'application': False,
}
