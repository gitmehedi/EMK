# -*- coding: utf-8 -*-
{
    'name': "Stock Purchase Report",

    'summary': """
        Custom Report For Stock Purchase""",

    'description': """
        This Here we can be able to print purchase data for selected period by Vendor.
    """,

    'author': "Genweb2",
    'website': "http://www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': [
        'stock_picking_mrr',
        'report_layout',
    ],

    'data': [
        # 'security/ir.model.access.csv',
        'wizard/purchase_report_wizard_view.xml',
        'report/purchase_report_template.xml',
    ]
}