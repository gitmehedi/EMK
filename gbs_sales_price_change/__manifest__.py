{
    'name': 'GBS Sales Price Change',
    'version': '1.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles request of changing Product Sale Price",
    'depends': [
        'gbs_application_group',
        'sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/sales_price_security.xml',
        'wizards/sale_price_change_wizard_view.xml',
        'views/sale_price_change_history.xml',
        'views/sale_price_change_view.xml',
        'views/inherited_products_view.xml',
        'views/product_packaging_mode_view.xml',
    ],
    'installable': True,
    'application': True,
}
