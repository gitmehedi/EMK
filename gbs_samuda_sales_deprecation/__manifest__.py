# -*- coding: utf-8 -*-
{
    'name': "GBS Sales Deprecation",
    'summary': """Deprecated Customer, Product Variant, Packing Modes will not be shown on relevant
                    combo at new SO & PI Creation.""",
    'author': "Genweb2",
    'website': "www.genweb2.com",
    'category': 'Sales',
    'version': '10.0.0.1',
    'depends': [
        'base',
        'product',
        'product_sales_pricelist',
        'gbs_pi_creation'
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/product_view.xml',
        'views/product_packaging_mode_view.xml',
        'views/sale_view.xml'
    ]
}
