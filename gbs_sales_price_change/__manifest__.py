{
    'name': 'GBS Sales Price Change',
    'version': '1.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles request of changing Product Sale Price",
    'depends': [
        'sale',
        'product',
    ],
    'data': [
        'security/sales_price_security.xml',
        'security/ir.model.access.csv',
        'views/sale_price_change_history.xml',
        'views/sale_price_change_view.xml',
        'views/inherited_products_view.xml',



    ],
    'installable': True,
    'application': True,
}
