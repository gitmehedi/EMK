# -*- coding: utf-8 -*-
{
    'name': "Rent Agreement",
    'description': """
        Module is responsible for 'Rent Agreement'.This module included with-
        1. Creation / Modification of Rent Agreement
        2. Deletion of Rent Agreement
        3. Accounting Treatment of Rent Agreement
        4. Amendment of Rent Agreements


        """,
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'vendor_advance_ou',
        'account_fiscal_month',
        'account_fiscal_year'
    ],
    'data': [
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/rent_agreement_view.xml',
        'wizard/rent_amendment_wizard_view.xml',
        'wizard/agreement_warning_wizard.xml',
        'wizard/vendor_bill_generation_batch_wizard.xml',
        'views/vendor_bill_generation_view.xml',
        'data/rent_agreement_exprie_scheduler.xml'
        # 'views/menu.xml'

    ],
    'installable': True,
    'application': False
}