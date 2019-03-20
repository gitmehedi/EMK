# -*- coding: utf-8 -*-
{
    'name': "Stock Picking Loan",

    'summary': """
        This module link stock picking and loan mangement""",

    'description': """
        In stock picking loan option available.
        By this module user can select product as per loan raise.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Inventory',
    'version': '10.0.1',

    'depends': ['stock_picking_extend',
                'gbs_samuda_stock',
                'item_loan_process'],
    'data': [
        'views/stock_picking_views.xml',
        'views/item_loan_borrowing_views.xml',
        'views/item_loan_lending_views.xml',
    ],
}