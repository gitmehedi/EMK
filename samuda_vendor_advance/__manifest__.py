# -*- coding: utf-8 -*-
{
    'name': "Vendor Advances",
    'description': """ Vendor Advances for Samuda""",
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'account_accountant',
    ],
    'data': [
        'data/data_vendor_advance.xml',
        'security/ir.model.access.csv',
        'views/vendor_advance_view.xml'
    ],
    'installable': True,
    'application': False,
}
