# -*- coding: utf-8 -*-
{
    'name': 'Payment Instruction',
    'summary': 'Payment Instruction Module',
    'description': """ Payment Instruction module to save the record.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting',
    'depends': [
        'account',
        'sub_operating_unit',
        'vendor_advance',
        'rent_agreement',
        'vendor_security_deposit',
        'gbs_res_partner',
        'account_fam'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/payment_instruction_view.xml',
        'wizard/payment_instruction_wizard_view.xml',
        'views/account_invoice.xml',
        'views/vendor_advance.xml',
        'views/security_return.xml',
        'views/inherit_vendor_bill_generation_view.xml'
    ],
    'installable': True,
    'application': True,
}
