# -*- coding: utf-8 -*-
{
    'name': "GBS Purchase CNF Quotation",

    'summary': """
        CNF Type Quotation""",

    'description': """
        Manage the quotation of services related product, CNF type quotation.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Inventory',
    'version': '10.0.1',

    'depends': ['purchase'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_quotation_cnf_views.xml',
    ],

}