{
    'name': 'GBS Accounting Installer',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting',
    'depends': ['account_accountant',
                'account_parent',
                'account_type_menu',
                'account_operating_unit',
                'account_fiscal_year',
                'account_move_fiscal_year',
                'buff_partner_bank_branch',
                'account_invoice_supplier_ref_unique'],

    'data': [ ],
    'description': 'Install all modules which is related to Accounting',
    'installable': True,
    'application' : True,
}