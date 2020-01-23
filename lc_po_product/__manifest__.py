{
    'name': 'Product of LC',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'10.0.1.0.0',
    'depends': [
        'letter_of_credit',
        'gbs_purchase_order',
    ],

    'data': [
        'views/lc_product.xml',
        'views/inherited_purchase_order_view.xml',
    ],
    'summary': 'Product of LC',
    'installable': True,
    'application': False,
}