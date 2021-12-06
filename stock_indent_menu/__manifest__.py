{
    'name': 'Stock Indent Menu',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Indent Product',
    "sequence": 10,
    'summary': 'Install all modules inside Indent functionality',
    'description': """
    Install all modules inside Indent functionality.
    """,
    'depends': [
        'stock_indent_access',
    ],
    'data': [
        'views/menu.xml'
    ],
    'installable': True,
    'application': True,
}
