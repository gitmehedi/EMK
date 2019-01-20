# -*- coding: utf-8 -*-
{
    'name': "TDS Vendor Challan",
    'description': """
        Module is responsible for 'TDS & Vat Supplier Challan'.This module included with-
        --Selection wizard
    
        """,
    'author': "Genweb2",
    'website': "http://www.genweb2.com",
    'category': 'Account',
    'version': '10.0.0.1',
    'depends': ['account_tds',
                'sub_operating_unit'
                ],

    'data': [
        # 'security/ir.model.access.csv',
        'wizards/tds_challan_selection_wizard.xml',
        'views/tds_account_move_line_view.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'application': True,
}
