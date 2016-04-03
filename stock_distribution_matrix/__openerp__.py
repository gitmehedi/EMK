# -*- coding: utf-8 -*-
{
    'name': "Stock Distribution Matrix",

    'summary': """
        Product Distribution Matrix module allow you to Distribute product with matrix input 
        """,

    'description': """
Quick and Easy
===========================

This module allows to manager Stock Distribution Matrix.

    """,

    'author': "Genweb2 Ltd.",
    'website': "http://www.genweb2.com",
    'category': 'Stock',
    'version': '0.1',
    'data': [
            'security/ir.model.access.csv',
            'views/inventory_distribution_to_shop.xml',
              ],
    'depends': ['stock', 'web_widget_distribution_matrix'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
