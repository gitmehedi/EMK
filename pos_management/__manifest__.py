# -*- coding: utf-8 -*-
{
    'name': "EMK Point of Sale",
    'summary': """
        Custom Point of Sale""",
    'description': """
        To manage the purchase order,quotation and revision . 
    """,

    'author': "Genweb2 Limited",
    'website': "https://www.genweb2.com",

    'category': 'Point_of_Sale',
    'version': '10.0.1',
    'depends': [
        'point_of_sale',
        'account',
        'pos_users',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_category_view.xml',
        'views/product_view.xml',
        'views/account_bank_statement_views.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
}
