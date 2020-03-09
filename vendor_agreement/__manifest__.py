# -*- coding: utf-8 -*-
{
    'name': "Vendor Agreement",
    'description': """
        Module is responsible for 'Vendor Agreement'.This module included with-
        1. Creation / Modification of Agreement
        2. Deletion of Agreement
        3. Agreement Amendment
        4. Agreement Postponed and Resume
        5. Payment Instruction Against Agreement
        6. Adjustment History (if any)

        """,
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'agreement_account',
        'gbs_vendor_bill',
    ],
    'data': [
        'data/data.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'wizards/amendment_agreement_view.xml',
        'wizards/vendor_agreement_payment_instruction_wizard_view.xml',
        'wizards/rent_payment_instruction_wizard_view.xml',
        'wizards/invoice_merge_view.xml',
        'views/vendor_agreement_view.xml',
        'views/rent_agreement_view.xml',
        'views/account_invoice_view.xml',
        'views/payment_instrauction_view.xml',
    ],
    'installable': True,
    'application': True,
}
