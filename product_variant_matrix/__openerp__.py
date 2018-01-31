# -*- coding: utf-8 -*-
{
    'name': "Product Variant Matrix",
    'author': 'Genweb2 Limited',
    'website': "http://www.genweb2.com",
    'category': 'Product',
    'version': '0.1',
    'summary': """ 
        Product Variant Matrix module allow you to 
        create product with matrix input 
        """,
    'description': """ This module allows to manager product variant. """,
    'data': [
        'default_data/product_extend_data.xml',
        'views/inherited_product_template.xml',
    ],
    'depends': ['product',
                'account',
                'stock',
                'point_of_sale',
                'web_widget_x2many_2d_checkbox'
                ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
