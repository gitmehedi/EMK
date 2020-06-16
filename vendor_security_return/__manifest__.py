# -*- coding: utf-8 -*-
{
    'name': "Drop Vendor Security Deposit return",
    'description': """
        Module is responsible for 'Return of SD'.This module included with-
        1. Creation / Modification of Security Deposit Return
        2. Deletion of Security Deposit Return
        3. Return Security Deposit of multiple advance payment at a single time
        4. Manual amount input for multiple advance amount 

        """,
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'agreement_account',
        'gbs_vendor_bill',
        'vendor_agreement'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/security_deposit.xml'
    ],
    'installable': True,
    'application': True,
}