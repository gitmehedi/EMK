# -*- coding: utf-8 -*-
{
    'name': 'GBS Reverse Bill',
    'description': """ Extended module to reverse Vendor Bill.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting',
    'depends': [
        'asset_vendor_bill',
        # 'tds_vat_challan',
    ],
    'data': [
        'wizards/account_invoice_refund_view.xml',
        'views/account_invoice_view.xml',

    ],
    'installable': True,
    'application': True,
}