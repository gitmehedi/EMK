# -*- coding: utf-8 -*-

{
    'name': 'Inventory Installation',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Module Installation',
    'summary': 'Install all inventory related module',
    'description': 'Install all inventory related module',
    'version': '1.0',
    'depends': [
        "stock_indent",
        "stock_indent_access",
        "stock_indent_menu",
        "stock_indent_install",
        "indent_type",
        "emk_purchase_order",
        "emk_purchase_order_access",
        "emk_purchase_order_menu",
        "emk_purchase_order_install",
        "stock_indent_menu",
        "emk_purchase_order_menu",
        "stock",
        "stock_account",
    ],
    'installable': True,
    'application': True,
}
