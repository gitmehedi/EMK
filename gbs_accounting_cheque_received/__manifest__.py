{
    'name': 'Cheque Received',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'version':'10.1.1.1',

    'depends': [
        'gbs_application_group',
        'sale',
        'account',
        'custom_report',
    ],

    'data': [
        'views/cheque_received_view.xml',
        'views/cheque_list_not_honoured.xml',
        'views/money_receipt_sequence_view.xml',
        'views/inherit_accounts_config_settings_view.xml',
        'report/gbs_hr_payroll_report.xml',
        'report/payroll_report_view.xml',
    ],

    'summary': 'Cheque Received',
    'installable': True,
    'application': False,
}