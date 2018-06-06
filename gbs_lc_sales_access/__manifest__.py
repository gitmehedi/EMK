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
                'gbs_application_group',
                'commercial',
                'letter_of_credit',
                'com_shipment',
                'shipment_lc_product',
                'gbs_document_type',
                'lc_sales_product',
                'gbs_pi_creation',
                'sale',
                'account',
                'sale_order_type'
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        # 'views/menu_items.xml',
    ],
}