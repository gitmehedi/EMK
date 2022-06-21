{
    'name': 'Vendor Bill Payment',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Account',
    'version': '10.1.1.1',
    'depends': [
        'account',
    ],

    'data': [
        'views/inherited_account_payment_view.xml',
        'views/inherited_account_config_settings.xml'
    ],

    'summary': 'Vendor Bill Payment',
    'description':
    """Vendor Bill Payment""",
    'installable': True,
    'application': False,
}