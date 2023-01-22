# -*- coding: utf-8 -*-
{
    'name': "Vendor Advances",
    'description': """
        Module is responsible for 'Vendor Advances'.This module included with-
        1. Creation / Modification of Vendor Advances
        2. Deletion of Vendor Advances
        3. Accounting Treatment of Vendor Advances
        

        """,
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'account_accountant',
        'l10n_bd_account_tax',
        'vendor_security_deposit',
    ],
    'data': [
        'data/data.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/vendor_advance_view.xml',
        'views/account_invoice.xml',
        'views/receive_outstanding_advance.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
}