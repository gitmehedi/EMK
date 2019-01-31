# -*- coding: utf-8 -*-
{
    'name': 'Account TDS',
    'description': """
        Module is responsible for 'Tax Deducted at Source'.This module included with-
        --TDS nature/rules
        --TDS version history
        --Fiscal year/month for TDS
        --TDS current rate report
        --TDS applicable to product
        --TDS applicable to vendor bill
        """,
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Account',
    'depends': [
        'account',
        'date_range',
        'product',
        'account_operating_unit',
    ],
    'data': [
        'data/tds_version_scheduler.xml',
        'security/ir_security.xml',
        'security/ir.model.access.csv',
        'wizards/amendment_tds_rule.xml',
        'views/account_tds_rule_view.xml',
        'views/inherit_date_range_view.xml',
        'views/account_invoice_view.xml',
        'views/inherit_product_template.xml',


    ],
    'installable': True,
    'application': True,
}
