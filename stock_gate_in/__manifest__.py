# -*- coding: utf-8 -*-
{
    'name': "Stock Gate In",

    'summary': """
        Extend Module to link Stock and Gate In""",

    'description': """
        
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': [
        'com_shipment',
        'stock_operating_unit',
        'ir_sequence_operating_unit',
        'stock_picking_lc',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_gate_in_view.xml',
        'data/gate_in_sequence.xml'
    ],
    'installable': True,
    'application': False,

}