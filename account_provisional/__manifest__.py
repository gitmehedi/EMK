# -*- coding: utf-8 -*-
{
    'name': 'Account Provisional Expenses',
    'description': """
        Module is responsible for 'Provisional Expenses'.This module included with-
        --Provisional Automation(Scheduler)
        --Calculate Provisional Expenses
        --Provisional Journal Entry
        --Record of Provisional Expenses
        """,
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Account',
    'depends': [
        'account',
        'product',
        'date_range',
        'account_operating_unit',
    ],
    'data': [
        'data/provisional_scheduler.xml',
        'data/provesional_expenses_journal_data.xml',
        # 'security/ir_security.xml',
        # 'security/ir.model.access.csv',
        'views/inherit_product_view.xml',
    ],
    'installable': True,
    'application': True,
}
