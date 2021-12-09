{
    'name': 'EMK Purchase Order Menu',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Purchase Product',
    "sequence": 10,
    'summary': 'Install all modules inside purchase order functionality',
    'description': """
    Install all modules inside purchase order functionality.
    """,
    'depends': [
        'emk_purchase_order_access',
    ],
    'data': [
        'views/menu.xml'
    ],
    'installable': True,
    'application': True,
}
