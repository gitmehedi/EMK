# -*- coding: utf-8 -*-
{
    'name': 'Drop GBS Vendor Bill',
    'description': """ Extended module to manage Vendor Bill.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting',
    'depends': [
        'account_invoice_merge_attachment',
        'account_operating_unit',
        'base_suspend_security',
        'gbs_payment_instruction',
        'gbs_res_partner',
    ],
    'data': [
        'security/security.xml',
        'data/bill_payment_instruction_scheduler.xml',
        'wizards/bill_payment_instruction_wizard.xml',
        'views/account_config.xml',
        'views/invoice_merge_view.xml',
        'views/account_invoice_view.xml',
        'views/payment_instructions_view.xml',
    ],
    'installable': True,
    'application': True,
}