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
        'account',
        'gbs_sales_commission',
        'delivery_order',
        'sales_team',
        'gbs_sales_delivery_goods',
        'customer_credit_limit',
        'sale',
        'gbs_procure_n_commercial_access',
        'sales_team_operating_unit',
        'product_sales_pricelist',
    ],


    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/lc_sales_comm_acc.xml',
        'views/menu_items.xml',

    ],
}