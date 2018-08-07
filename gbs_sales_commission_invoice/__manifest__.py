{
    'name': 'Customer Commission on Invoices',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Sales',
    'depends': [
        'account',
        'sale', # for inheriting invoice line creation method
    ],
    'data': [
        'views/inherited_account_invoice_line_view.xml',
        ],
    'description': 'This module adds Customer Commission to Account Invoice Line',
    'installable': True,
    'application': True,
}
