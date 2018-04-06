# -*- coding: utf-8 -*-
{
    'name': "Stock Picking MRR",

    'summary': """
        This module relate Stock Picking to MRR.
    """,

    'description': """
        After Picking done there approval process for MRR is added by this module.
        Also print option available. User can print MRR by this module.  
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.0.1',

    'depends': ['stock_picking_extend'],

    'data': [
        # 'security/ir.model.access.csv',
        'data/sequence.xml',
        'report/template_mrr.xml',
        'views/stock_picking_views.xml',
    ],

}