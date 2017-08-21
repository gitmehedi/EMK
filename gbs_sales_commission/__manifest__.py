{
    'name': 'GBS Sales Commission',
    'version': '1.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Sales',
    'depends': [
        'sale',
        'sales_team',
    ],
    'data': [
        'views/inherited_res_partner_views.xml',
        'views/inherited_sale_order_views.xml',
        'views/customer_commission_configuration_views.xml',
        ],
    'description': 'GBS Sales Commission',
    'installable': True,
    'application': True,
}
