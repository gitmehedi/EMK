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
    'depends': ['stock','stock_operating_unit'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
}