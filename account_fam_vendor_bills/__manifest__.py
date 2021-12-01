# -*- coding: utf-8 -*-
{
    'name': 'Fixed Assets Vendor Bills',
    'description': """ Main module for asset management which include all css,js and image files.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Accounting Assets',
    "depends": [
        'account',
        'analytic',
        'account_parent',
        'account_operating_unit',
        'account_fam_menu',
    ],
    "data": [
        'wizard/product_product_wizard_view.xml',
        'wizard/cost_centre_wizard_view.xml',
        'views/cost_centre_view.xml',
        'views/inherit_product_product_view.xml',
    ],
    'installable': True,
    'application': True,
}
