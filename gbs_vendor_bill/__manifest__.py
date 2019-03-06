# -*- coding: utf-8 -*-
{
    'name': 'GBS Vendor Bill',
    'description': """ Extended module to manage Vendor Bill.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting',
    'depends': [
        'account_invoice_merge_operating_unit',
        'account_invoice_merge_attachment',
        'account_mtbl',
        'gbs_payment_instruction',
    ],
    'data': [
        'data/bill_payment_instruction_scheduler.xml',
        'wizards/bill_payment_instruction_wizard.xml',
        'views/product_product_view.xml',
        'views/invoice_merge_view.xml',
        'views/account_invoice_view.xml',

    ],
    'installable': True,
    'application': True,
}