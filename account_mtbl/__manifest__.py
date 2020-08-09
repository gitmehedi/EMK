# -*- coding: utf-8 -*-

{
    "name": "MTBL GL Master Data",
    "summary": "Master Data of mtbl",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        'account',
        'analytic',
        'account_parent',
        'account_type_menu',
        'account_type_inactive',
        'l10n_bd_account_tax',
        'account_operating_unit',
        'account_fiscal_year',
        'account_fiscal_month',
        # 'payment',
        'gbs_account_level',
        'sub_operating_unit',
        'vendor_advance_ou',
        'rent_agreement',
        'mtbl_access',
        'gbs_res_partner',
        'account_tax_challan'
        # 'account_tds'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'security/security.xml',
        # 'data/default_data.xml',
        'views/menu_view.xml',
        'wizard/segment_wizard_view.xml',
        'wizard/branch_wizard_view.xml',
        'wizard/res_partner_bank_wizard_view.xml',
        'wizard/res_currency_wizard_view.xml',
        'wizard/product_product_wizard_view.xml',
        'wizard/account_tag_wizard_view.xml',
        'wizard/account_journal_wizard_view.xml',
        'wizard/account_type_wizard_view.xml',
        'wizard/sevicing_channel_wizard_view.xml',
        'wizard/acquiring_channel_wizard_view.xml',
        'wizard/account_analytic_account_wizard_view.xml',
        'wizard/account_account_wizard_view.xml',
        'wizard/res_currency_rate_wizard_view.xml',
        'wizard/inherit_account_tax_wizard_view.xml',
        'wizard/account_period_close_view.xml',
        'wizard/account_period_type_wizard_view.xml',
        'wizard/account_period_wizard_view.xml',
        'views/inherited_account_tax.xml',
        'views/report_view_access.xml',
        'views/act_window_access.xml',
        'views/segment_view.xml',
        'views/servicing_channel_view.xml',
        'views/res_partner_bank_view.xml',
        'views/account_tag_view.xml',
        'views/acquiring_channel_view.xml',
        'views/inherit_res_currency_view.xml',
        'views/inherit_account_journal_view.xml',
        'views/inherit_res_bank_view.xml',
        'views/inherit_account_move_cbs_view.xml',
        'views/inherit_account_move_ogl_view.xml',
        'views/inherit_account_move_view.xml',
        'views/branch_view.xml',
        'views/inherit_account_account_view.xml',
        'views/inherit_account_type_view.xml',
        'views/inherit_product_product_view.xml',
        'views/inherit_analytic_account_view.xml',
        'views/account_analytic_account_view.xml',
        'views/res_users_preferences_view.xml',
        'views/inherit_res_currency_rate_view.xml',
        'views/inherit_vendor_advance_view.xml',
        'views/account_report.xml',
        'views/account_invoice_view.xml',
        'views/inherit_res_partner_view.xml',
        'views/inherit_account_config_view.xml',
        'views/inherit_vendor_security_deposit_view.xml',
        'views/date_range_type_view.xml',
        'views/date_range_view.xml',
        'views/inherit_tds_vat_payment_view.xml',
        'wizard/inherit_tds_vat_move_payment_wizard.xml',
        'views/receive_outstanding_advance_view.xml'
    ],
    'installable': True,
    'application': True,
}
