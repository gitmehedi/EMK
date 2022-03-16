# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account FX Revaluation",
    "summary": "Account FX Revaluation",
    'category': 'Accounting',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    "depends": [
        "account_accountant",
        "account_fiscal_year",
        "account_operating_unit",
        "account_currency_wrapper"
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/menu_view.xml',
        'views/inherit_account_currency_view.xml',
        'views/inherit_account_config_view.xml',
        'views/account_fx_revaluation_view.xml',
        'views/inherit_account_account_view.xml'
    ],
    "application": True,
    "installable": True,
}
