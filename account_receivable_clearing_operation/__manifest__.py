{
    'name': 'Account Receivable Clearing Operation',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'version':'10.0.1.0.0',
    'depends': [
        'account',
        'gbs_account',
        'gbs_accounting_cheque_received',
        'delivery_order',
    ],

    'data': [

        'views/security.xml',
        'wizards/unreconciled_entry_wizard_view.xml',
        'views/inherited_res_company_view.xml',
        'views/account_move_line.xml',
        'views/payment_entry_reconciled_view.xml',
    ],

    'summary': 'Account Receivable Clearing Operation',
    'installable': True,
    'application': False,
}