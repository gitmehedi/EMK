# -*- coding: utf-8 -*-
{
    'name': "Product Variant History",

    'summary': """
        History Of Purchased Product Average""",

    'description': """
        This module save the history record of all product purchased price variant wise
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Product',
    'version': '10.0.1',

    'depends': ['product'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_variant_history_views.xml',
    ],
}