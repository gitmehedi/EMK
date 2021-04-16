{
    'name': 'GBS Expense Accounting Installer',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting',
    'depends': [
                'l10n_bd_account_tax',
                'account_tax_challan',
                'samuda_vendor_bill',
                'gbs_vendor_payment',
                ],

    'data': [ ],
    'description': 'Install all modules which is related to Expense Accounting',
    'installable': True,
    'application' : True,
}