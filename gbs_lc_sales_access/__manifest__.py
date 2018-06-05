# -*- coding: utf-8 -*-
{
    'name': "LC Sales Access",

    'summary': """
        This module will install base required addons.""",

    'description': """
        This module will install base required addons.
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    'depends': ['base',
                'commercial',
                'letter_of_credit',
                'com_shipment',
                'gbs_application_group',
                'shipment_lc_product',
                'lc_sales_product',
                'lc_po_product'
    ],


    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/menu_items.xml',
    ],
}