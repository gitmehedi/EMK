{
    'name': 'GBS Accounting Installer',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting',
    'depends': ['account',
                'analytic',
                'mtbl_access',
                'account_asset',
                'account_budget',
                'account_cancel',
                'account_parent',
                'account_type_menu',
                'account_type_inactive',
                'account_accountant',
                'account_fiscal_year',
                'account_fiscal_month',
                'account_move_fiscal_year',
                'base_vat_bd',
                'sub_operating_unit',
                'ou_currency',
                'gbs_res_partner',
                'account_tds',
                'vendor_agreement',
                'gbs_vendor_bill',
                'tds_vendor_challan',
                'account_mtbl',
                #'account_move_fiscal_month',
                #'account_operating_unit',
                #'base_bank_bd',
                #'account_check_printing',
                #'account_invoice_supplier_ref_unique',
                #'account_financial_report_qweb',
                #'customer_activity_statement',
                #'customer_outstanding_statement',
                #'account_journal_report',
                #'custom_amount_conversion',
                #'cheque_printing',
                #'account_invoice_merge',
                #'account_invoice_merge_operating_unit',
                #'account_invoice_merge_attachment',
                ],

    'data': [ ],
    'description': 'Install all modules which is related to Accounting',
    'installable': True,
    'application' : True,
}