# -*- coding: utf-8 -*-
{
    'name': "Stock Distribution Matrix",
    'author': 'Genweb2 Limited',
    'website': "http://www.genweb2.com",
    'category': 'Stock',
    'version': '0.1',
    'summary': """
        Product Distribution Matrix module allow you to Distribute product with matrix input 
        """,
    'description': """""",
    'depends': ['stock',
                'point_of_sale',
                'web_widget_distribution_matrix',
                'purchase_order_pebbles',
                'pebbles_transfer_user',
                'custom_report',
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/menu.xml',
        'views/inventory_distribution_to_shop.xml',
        'views/inherited_stock_inventory.xml',
        'views/inherited_pos_config_view.xml',
        'views/inherited_purchase_order_view.xml',
        'views/stock_view.xml',
        'views/warehouse_to_shop_distribution.xml',
        'reports/stock_distribution_to_shop_views.xml',
        'reports/purchase_order_quantity_menu.xml',
        'reports/purchase_order_quantity_views.xml',
        'reports/challan_report_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
