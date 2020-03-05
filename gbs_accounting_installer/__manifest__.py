{
    'name': 'GBS Accounting Installer',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting',
    'depends': ['account_cancel',
                'account_parent',
                'account_type_menu',
                'account_type_inactive',
                'account_accountant',
                'account_fiscal_year',
                'account_fiscal_month',
                'account_move_fiscal_year',
                'account_move_fiscal_month',
                'account_operating_unit',
                'base_bank_bd',
                'account_check_printing',
                'account_invoice_supplier_ref_unique',
                'account_financial_report_qweb',
                'customer_activity_statement',
                'customer_outstanding_statement',
                'account_journal_report',
                'cheque_printing',
                'account_invoice_merge',
                'account_invoice_merge_operating_unit',
                #'account_receivable_clearing_operation',
                'gbs_account',
                "account_standard_report",
                "gbs_account_journal_log",
                'gbs_voucher',
                'account_parent_inherit',
                'gbs_analytic_account_type',
                'gbs_account_payment_narration',
                'gbs_general_ledger_customer',
                'gbs_journal_type',
                ],

    'data': [ ],
    'description': 'Install all modules which is related to Accounting',
    'installable': True,
    'application' : True,
}