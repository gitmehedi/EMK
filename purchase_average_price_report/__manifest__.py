# -*- coding: utf-8 -*-
{
    'name': "Product Purchase Average Price Report",

    'summary': """
        Purchase Price Average history Product Variant wise. 
    """,

    'description': """
        By this module user can see the record of Purchase 
        Price Average history Products Variant wise.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Product',
    'version': '10.0.1',

    'depends': ['stock','report_layout'],

    'data': [
        # 'security/ir.model.access.csv',
        'report/purchase_average_price_report_temp.xml',
        'wizard/purchase_average_price_wizard_view.xml',
    ],
}