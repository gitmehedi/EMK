# -*- coding: utf-8 -*-
{
    'name': "Stock Gate Out",

    'summary': """
        Extend Module to link Stock and Gate Out""",

    'description': """

    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': [
        'stock',
        'ir_sequence_operating_unit'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_gate_out_view.xml',
        'data/gate_out_sequence.xml'
    ],
    'installable': True,
    'application': False,

}