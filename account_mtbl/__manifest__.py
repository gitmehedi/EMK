# -*- coding: utf-8 -*-

{
    "name": "MTBL GL Master Data",
    "summary": "Master Data of mtbl",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        'base',
        'mail',
        'product',
        'portal',
        'account',
        'analytic',
        'payment',
        'mtbl_access',
        'account_parent',
        'account_operating_unit',
        'account_type_inactive',
        'account_fiscal_year',
        'operating_unit',
        'gbs_account_level',
        # 'account_tds'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
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
    ],
    'installable': True,
    'application': True,
}
