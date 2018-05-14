{
    'name': 'Custom Currency Conversion',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'account',
    'version':'10.1.1.1',
    'depends': [
        'account',
    ],

    'data': [
        'views/inherit_account_invoice_view.xml',
    ],

    'summary': 'Convert foreign currencies on a given conversion rate',
    'installable': True,
    'application': False,
}