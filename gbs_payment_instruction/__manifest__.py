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
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
