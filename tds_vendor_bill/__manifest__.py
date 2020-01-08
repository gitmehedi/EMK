# -*- coding: utf-8 -*-
{
    'name': 'TDS Vendor Bill',
    'description': """
        Linked module of Account TDS and Vendor Bill
        """,
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'account_tds',
        'gbs_vendor_bill',
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'application': True,
}
