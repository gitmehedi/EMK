# -*- coding: utf-8 -*-
{
    'name': 'MRP BOM Product User',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Manufacturing',
    'version': '10.0.1.0.0',
    'depends': [
        'mrp'
    ],
    'data': [
        'views/product_view.xml',
        'views/res_users_view.xml',
    ],
    'summary': 'Relational Module Of Product and User for BOM/MO',
    'description': """
        By this moduel user account will mapped by Product. So that user only access Product BOM/MO who has mapped by user account. 
    """,
    'installable': True,
    'application': False,


}