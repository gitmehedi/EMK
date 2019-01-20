# -*- coding: utf-8 -*-
{
    'name': "TDS Vendor Challan",
    'description': """
        Module is responsible for 'TDS & Vat Supplier Challan'.This module included with-
        --Selection wizard
    
        """,
    'author': "genweb2",
    'website': "http://www.genweb2.com",
    'category': 'Vendor',
    'version': '0.1',
    'depends': ['base',
                'sub_operating_unit',
                'mail'
                ],

    'data': [
        # 'security/ir.model.access.csv',
        'wizards/tds_challan_selection_wizard.xml',
        'views/tds_vendor_challan.xml',
    ],
    'installable': True,
    'application': True,
}
