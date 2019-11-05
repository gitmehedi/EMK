{
    'name': 'GBS Expense Accounting Installer',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting',
    'depends': [
                'gbs_vendor_bill',
                'base_vat_bd_rebate',
                'tds_vat_challan',
                'tds_vendor_bill',
                'account_tds',
                ],

    'data': [ ],
    'description': 'Install all modules which is related to Expense Accounting',
    'installable': True,
    'application' : True,
}