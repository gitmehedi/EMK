{
    'name': 'Stock Indent Access Rights',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Indent Product',
    "sequence": 10,
    'summary': 'All Access Rights of Stock Indent Module',
    'description': """
This application allows you to easily maintain access rights of emk process.
""",
    'depends': [
        'base',
        'account',
        'account_parent',
        'user_access_invisible',
    ],
    'data': [
        'security/ir_security.xml',
        'views/menu.xml'
    ],
    'installable': True,
    'application': True,
}
