{
    'name': 'Product Income Account',
    'version': '10.1.0.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'depends': [
        'product',
        'samuda_so_type',
    ],

    'data': [
        #'security/ir.model.access.csv',
        #'security/sales_price_security.xml',
        'views/inherit_product_product.xml',
    ],

    'installable': True,
    'application': False,
}
