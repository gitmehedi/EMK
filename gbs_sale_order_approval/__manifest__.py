{
    'name': 'GBS Sale Order Approval Process',
    'version': '1.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles Sale Order requisition in a customized business logic way.",
    'depends': [
        'sale',
        'product',
    ],
    'data': [
        'views/inherited_sale_view.xml',

    ],
    'installable': True,
    'application': True,
}
