{
    'name': 'Samuda Account',
    'version': '10.1.0.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "",
    'depends': [
        'account',
        'samuda_so_type'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_type_product_acc.xml',
    ],
    'installable': True,
    'application': True,
}
