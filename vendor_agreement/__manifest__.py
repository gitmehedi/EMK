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
    'author': "Genweb2",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Vendor',
    'depends': ['agreement_account'],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizards/amendment_agreement.xml',
        'views/vendor_agreement_view.xml',
        ],
    'installable': True,
    'application': True,
}
