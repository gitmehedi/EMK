{
    'name': 'Payment Collection',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Account',
    'version':'10.1.1.1',
    'depends': [
        'account',
    ],

    'data': [
        'views/inherited_account_payment_view.xml',
        'security/ir.model.access.csv',
    ],

    'summary': 'Payment Collection',
    'description':
    """Payment Collection""",
    'installable': True,
    'application': False,
}