# -*- coding: utf-8 -*-
{
    'name': "BD Account Tax",
    'description': """BD Account Tax""",
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'account',
        'date_range',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/tds_date_range_type.xml',
        'views/inherit_date_range_view.xml',
        'views/inherit_account_tax_view.xml',
        'views/inherit_account_invoice_view.xml',
        'views/tax_menuitem.xml'
    ],
    'installable': True,
}