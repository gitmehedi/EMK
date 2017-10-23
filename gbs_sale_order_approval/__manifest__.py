{
    'name': 'Order to Cash Process',
    'version': '10.1.0.1',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles Sale Order requisition in a customized business logic way.",
    'depends': [
        'gbs_application_group',
        'sale',
        'product',
        'sales_team',
        'gbs_sales_commission',
        'gbs_sales_commission_so',
        'delivery_order',
        'sale_order_type',
        'operating_unit'
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/sale_order_approval_security.xml',
        'views/inherited_sale_view.xml',
        'views/inherited_sale_order_type_view.xml',
    ],
    'installable': True,
    'application': True,
}
