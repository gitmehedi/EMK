# -*- coding: utf-8 -*-
{
    'name': "GBS Supplier",

    'summary': """
        This module inherit module of base Partner module""",

    'description': """
        *This module define supplier category.
        *Define Supplier Type.
        *Define is it C&F or not.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Supplier',
    'version': '10.0.1',

    'depends': ['base'],

    'data': [
        'views/supplier_category.xml',
        'views/inherited_res_partner.xml',
    ],

}