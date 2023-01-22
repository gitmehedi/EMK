# -*- coding: utf-8 -*-
{
    'name': "Vendor Security Deposit Operating Unit",
    'description': """
                Vendor Security Deposit Operating Unit
        """,
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'vendor_security_deposit',
        'account_operating_unit'
    ],
    'data': [
        'views/vendor_security_deposit_view.xml',
        'views/inherit_account_config_view.xml'
    ],
    'installable': True,
    'application': False,
}