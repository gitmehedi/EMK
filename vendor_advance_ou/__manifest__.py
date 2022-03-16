# -*- coding: utf-8 -*-
{
    'name': "Vendor Advance Operating Unit",
    'description': """
                Vendor Advance Operating Unit
        """,
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'vendor_advance',
        'vendor_security_deposit_ou',
        'account_operating_unit'
    ],
    'data': [
        'views/vendor_advance.xml',
        'views/receive_outstanding_amount_view.xml'
    ],
    'installable': True,
    'application': False,
}