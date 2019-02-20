# -*- coding: utf-8 -*-
{
    'name': "TDS Vendor Challan",
    'description': """
        Module is responsible for 'TDS & Vat Supplier Challan'.This module included with-
        --Selection wizard
    
        """,
    'author': "Genweb2",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Vendor',
    'depends': ['mail',
                'account_tds',
                'sub_operating_unit',
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/tds_challan_selection_wizard.xml',
        'wizards/challan_deposited_wizard.xml',
        'wizards/challan_distributed_wizard.xml',
        'wizards/challan_ou_selection_wizard.xml',
        'views/tds_account_move_line_view.xml',
        'views/tds_vat_challan.xml',
        'views/account_config.xml',
    ],
    'installable': True,
    'application': True,
}
