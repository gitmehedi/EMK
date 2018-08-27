{
    'name': 'Cash Sales Accounts Treatment',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'version':'10.1.1.1',

    'depends': [
        'account',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/conf_property_credit_acc_view.xml',
    ],

    'summary': 'Cash Sales Accounts Treatment',
    'installable': True,
    'application': False,
}