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
    ],

    'data': [
        'views/cheque_received_view.xml',
        'views/cheque_list_not_honoured.xml',
        'views/money_receipt_sequence_view.xml',
    ],

    'summary': 'Cheque Received',
    'installable': True,
    'application': False,
}