# -*- coding: utf-8 -*-
{
    'name': "Product Cost Adjustment",
    'author': 'Genweb2 Limited',
    'website': "http://www.genweb2.com",
    'category': 'Stock',
    'version': '0.1',

    'summary': """
        Product Distribution Matrix module allow you to Distribute product with matrix input 
        """,

    'description': """
Quick and Easy
===========================

This module allows to manager Stock Distribution Matrix.

    """,


    'data': [
            'views/product_cost_adjustment_views.xml',
             ],
    'depends': ['stock', 'web_widget_distribution_matrix'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
