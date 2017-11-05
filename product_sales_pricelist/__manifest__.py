{
    'name': 'Product Sales Pricelist',
    'version': '10.1.0.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles request of changing Product Sale Price",
    'depends': [
        'hr',
        'gbs_application_group',
        'sale',
        'product',
        'sales_team',
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/sales_price_security.xml',
        'wizards/sale_price_change_wizard_view.xml',
        'views/sale_price_change_history.xml',
        'views/sale_price_change_view.xml',
        'views/inherited_products_view.xml',
        'views/product_packaging_mode_view.xml',
        'report/change_product_price_report.xml'
    ],
    'installable': True,
    'application': True,
}
