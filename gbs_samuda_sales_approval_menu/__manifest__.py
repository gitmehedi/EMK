# -*- coding: utf-8 -*-
{
    'name': "Samuda Sales Approval Menu",

    'summary': """
        All approval menu for different approver""",

    'description': """
        By this moduel different user get different approval menu for the different modules.
        --Sale Order
        --Delivery Authorization
        --Product Sales Pricelist
        --Customer Commission
        --Customer Credit Limit 
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Sales Management',
    'version': '10.0.1',

    'depends': [
        'gbs_sale_order_approval',
        'customer_credit_limit',
        ],

    'data': [
        'views/approver_action_menus.xml',
    ],

}