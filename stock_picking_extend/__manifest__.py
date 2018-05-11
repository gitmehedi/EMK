# -*- coding: utf-8 -*-
{
    'name': "Stock Picking Extend",
    'summary': """
        This module is inherited module of Picking""",
    'description': """
        This module manage QC, Gate Pass and Transfer type(In or out delivery).
    """,
    'author': "Genweb2",
    'website': "www.genweb2.com",
    'category': 'Stock',
    'version': '10.0.0.1',
    'depends': ['stock','stock_operating_unit','account'],
    'data': [
        # 'security/ir.model.access.csv',
        'report/inherit_stock_picking_report.xml',
        'wizard/inherit_stock_immediate_transfer_views.xml',
        'views/stock_picking_views.xml',
    ],
}