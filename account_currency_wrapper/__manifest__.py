# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Currency Wrapper",
    "summary": "USD to BDT as rate input",
    'category': 'Accounting',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    "depends": [
        'base',
    ],
    "data": [
        'views/inherit_res_currency_view.xml',
        'views/inherit_res_currency_rate_view.xml'
    ],
    "application": False,
    "installable": True,
}