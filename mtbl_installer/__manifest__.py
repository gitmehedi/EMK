{
    'name': 'GBS Accounting Installer',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting',
    'depends': ['account',
                'analytic',
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
                'account_operating_unit',
                'account_invoice_merge',
                'account_invoice_merge_operating_unit',
                'account_invoice_merge_attachment',
                'agreement_account',
                'account_mtbl',
                'base_vat_bd',
                'sub_operating_unit',
                'ou_currency',
                'gbs_res_partner',
                'account_tds',
                'tds_vat_challan',
                'gbs_vendor_bill',
                'vendor_agreement',
                'account_fam',
                'account_provisional',
                'mtbl_access',

                # 'account_move_fiscal_month',
                # 'base_bank_bd',
                # 'account_check_printing',
                # 'account_invoice_supplier_ref_unique',
                # 'account_financial_report_qweb',
                # 'customer_activity_statement',
                # 'customer_outstanding_statement',
                # 'account_journal_report',
                # 'custom_amount_conversion',
                # 'cheque_printing',

                ],

    'data': [],
    'description': 'Install all modules which is related to Accounting',
    'installable': True,
    'application': True,
}
