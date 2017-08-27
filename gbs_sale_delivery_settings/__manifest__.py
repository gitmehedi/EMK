{
    'name': 'Sales Order Delivery Settings',
    'version': '1.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles Delivery Order auto generation settings from Sales Settings view",
    'depends': [
        'gbs_application_group',
        'sale',
        'product',
        'sales_team',
        'gbs_sale_order_approval',
        'gbs_sales_commission',
        'gbs_sales_commission_so',
    ],
    'data': [
        #'security/ir.model.access.csv',
        #'security/sale_order_approval_security.xml',
        'views/inherited_sale_do_view.xml',
    ],
    'installable': True,
    'application': True,
}
