{
    'name': 'Sales Order Delivery Settings',
    'version': '10.0.1.0.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles Delivery Order auto generation settings from Sales Settings view",
    'depends': [
        'sale',
        'sales_team',
    ],
    'data': [
        'views/inherited_sale_do_view.xml',
    ],
    'installable': True,
    'application': False,
}
