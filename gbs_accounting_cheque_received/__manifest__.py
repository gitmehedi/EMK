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
        'report',
        'gbs_sale_order_approval',
        'amount_to_word_bd',
        'report_layout',
        'gbs_samuda_account_access'
    ],

    'data': [
        'security/security.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizards/journal_add_wizard_view.xml',
        'wizards/add_honoured_date_wizard_view.xml',
        'views/cheque_received_view.xml',
        'views/money_receipt_sequence_view.xml',
        'views/inherit_accounts_config_settings_view.xml',
        'views/inherited_account_move_line_view.xml',
        'report/gbs_money_receipt_paperformat.xml',
        'report/gbs_money_receipt_report_view.xml',
        'views/inherit_cheque_received_view.xml',
        'views/inherit_cheque_received_not_honoured.xml',
        'views/cheque_list_not_honoured.xml'


    ],

    'summary': 'Cheque Received',
    'installable': True,
    'application': False,
}