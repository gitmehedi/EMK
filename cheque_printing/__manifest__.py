{
    'name': 'Cheque Printing',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'version':'10.1.1.1',
    'depends': [
        'account',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/cheque_info_entry_view.xml',
    ],

    'summary': 'Cheque Printing',
    'installable': True,
    'application': False,
}