# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Financial Year Closing",
    "summary": "Financial Year Closing",
    'category': 'Accounting',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    "depends": [
        "account_fiscal_year",
    ],
    "data": [
        # 'security/ir.model.access.csv',
        # "data/data.xml",
        # "wizard/date_range_generator.xml",
        # "wizard/account_period_wizard_view.xml",
        # "wizard/account_period_type_wizard_view.xml",
        # "wizard/account_period_close_view.xml",
        # "views/menu_view.xml",
        # "views/date_range_view.xml",
        # "views/date_range_type_view.xml",
        "views/account_config.xml",
        "wizard/account_fiscalyear_close_view.xml",
    ],
    # "qweb": [
    #     "static/src/xml/date_range.xml",
    # ],
    "application": True,
    "installable": True,
}
