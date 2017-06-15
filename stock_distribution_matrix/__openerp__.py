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
    'description': """
        Quick and Easy
        ===========================
        
        This module allows to manager Stock Distribution Matrix.

        """,
    'depends': ['stock',
                'point_of_sale',
                'web_widget_distribution_matrix'
                ],
    'data': [
            'security/ir.model.access.csv',
            'views/inventory_distribution_to_shop.xml',
            'views/inherited_stock_inventory.xml',
            'views/inherited_pos_config_view.xml',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
