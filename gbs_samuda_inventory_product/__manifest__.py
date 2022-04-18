# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Inventory Product",

    'summary': """
        Inventory Advisor will be able to create edit products. Inventory Manager and User will have read access.
    """,

    'description': """
    """,

    'author': "Genweb2",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product', 'gbs_application_group', 'purchase', 'gbs_purchase_requisition'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/variant_inventory_custom_view.xml',
        'views/product_inventory_custom_view.xml',
        'views/inventory_custom_views.xml',
        'views/inherited_product_toggle_active.xml',
        'views/product_no_create_edit_inherit_action_view.xml',
    ],
}
