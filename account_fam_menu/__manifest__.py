{
    'name': 'Fixed Assets Management Menu',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Accounting Assets',
    "sequence": 10,
    'summary': 'Install all modules inside FAM functionality',
    'description': """
    Install all modules inside FAM functionality.
    """,
    'depends': [
        'account_fam_access',
    ],
    'data': [
        'views/menu.xml'
    ],
    'installable': True,
    'application': True,
}
