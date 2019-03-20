# -*- coding: utf-8 -*-
{
    'name': "GBS Stock Product",

    'summary': """
        Extend Module of Product and Stock""",

    'description': """
        Customize view for product
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Inventory',
    'version': '10.0.1',

    'depends': ['stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        # 'views/inherited_product_template_views.xml',
        # 'views/inherited_product_category_view.xml',
    ],

}