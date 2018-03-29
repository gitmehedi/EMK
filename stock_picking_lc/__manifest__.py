# -*- coding: utf-8 -*-
{
    'name': "Stock Picking LC",

    'summary': """
        This module relate Stock Picking and LC""",

    'description': """
        There is a module Stock Picking Extend which inherit Stock Picking module.
        By this module LC and Picking Extended module are relate to do lc related job.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.0.1',

    'depends': ['stock_picking_extend','com_shipment'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
}