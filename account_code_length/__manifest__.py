{
    'name': 'Account Code Length',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'accounting',
    'depends': [
        'account',
        'account_accountant'
    ],

    'data': [
        'views/account_code_length_view.xml',
    ],

    'description': 'Checks Account code length',
    'installable': True,
    'application': False,
}
