# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Sales Access",

    'summary': """
        This module will install for Samuda Sales Access addons.""",

    'description': """
        This module will install for Samuda Sales Access.  
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'product_harmonized_system',
        'gbs_application_group',
        'stock',
        'gbs_sales_commission',
        'delivery_order',
        'sales_team',
        'gbs_sales_delivery_goods',
        'customer_credit_limit',
        'sale',
        'sales_team_operating_unit',
        'product_sales_pricelist',
        'hidden_admin',
        'lc_sales_product_local',
        'gbs_payment_term',
    ],


    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/menu_items.xml',

    ],
}