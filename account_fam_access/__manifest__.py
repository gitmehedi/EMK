{
    'name': 'Fixed Assets Access Rights',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Accounting Assets',
    "sequence": 10,
    'summary': 'All Access Rights of Fixed Assets Module',
    'description': """
This application allows you to easily maintain access rights of mtbl process.
""",
    'depends': [
        'base',
        'account',
        'account_parent',
    ],
    'data': [
        'security/ir_security.xml',
        'views/menu.xml'
    ],
    'installable': True,
    'application': True,
}
