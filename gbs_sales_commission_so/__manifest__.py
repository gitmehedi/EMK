{
    'name': 'Customer Commission on Sales Order',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Sales',
    'depends': [
        'sale',
        'gbs_sales_commission',
    ],
    'data': [
        'views/inherited_sale_order_views.xml',
        ],
    'description': 'This module adds Customer Commission to Sales Orde line',
    'installable': True,
    'application': True,
}
