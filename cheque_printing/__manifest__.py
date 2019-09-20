{
    'name': 'Cheque Printing',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'version': '10.1.1.1',
    'depends': [
        'account',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/cheque_info_wizard_views.xml',
        #'views/cheque_pay_confirmation_view.xml',
        'views/cheque_info_entry_view.xml',
        'views/inherited_account_payment_view.xml',
        'reports/paperformat.xml',
        'reports/cheque_printing_report_view.xml',

    ],

    'summary': 'Cheque Printing & Journal Entry',
    'installable': True,
    'application': False,
}
