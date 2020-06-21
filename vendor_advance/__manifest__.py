# -*- coding: utf-8 -*-
{
    'name': "Drop Vendor Advances",
    'description': """
        Module is responsible for 'Vendor Advances'.This module included with-
        1. Creation / Modification of Vendor Advances
        2. Deletion of Vendor Advances
        3. Accounting Treatment of Vendor Advances
        4. Vendor Security Deposit creation
        5. Vendor Security Return
        6.  Accounting Treatment of Vendor Security Return
        

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
        'views/vendor_advance_view.xml',
        'views/account_invoice_view.xml',
        'views/vendor_security_return_view.xml'

    ],
    'installable': True,
    'application': True,
}