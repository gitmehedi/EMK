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

    'depends': [
        'purchase',
        'letter_of_credit',
        # 'com_shipment',
        'ir_sequence_operating_unit',
    ],

    'data': [
        # 'security/ir.model.access.csv',
        'data/cnf_sequence.xml',
        'views/purchase_quotation_cnf_views.xml',
    ],

}