{
    'name': 'MTB OGL Installer',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Installation',
    'depends': [
        "account",
        "account_accountant",
        "account_parent",
        "operating_unit",
        "account_operating_unit",
        "account_invoice_merge_attachment",
        "account_fiscal_month",
        "agreement_account",
        "date_range",
        "base_suspend_security",
        "account_type_menu",
        "account_type_inactive",
        "mtbl_access",
        "base_vat_bd",
        "ou_currency",
        "sub_operating_unit",
        "account_fiscal_year",
        "account_asset",
        "gbs_bd_division",
        "gbs_res_partner",
        "account_fam",
        "account_category",
        "account_tds",
        "tds_vat_challan",
        "gbs_payment_instruction",
        "gbs_vendor_bill",
        "tds_vendor_bill",
        "asset_vendor_bill",
        "vendor_agreement",
        "account_provisional",
        "account_mtbl",
        "gbs_ogl_cbs_interface",
        "inherit_date_range",
        "bgl_accounts",
        "gbs_account_level",
        "gbs_account_budget",
        "gbs_reverse_bill",
        "password_security",
        "auth_session_timeout",
        "limit_login_attempts",
        "web_login_theme",
        "app_odoo_customize",
        "account_reports_xls",
        "auto_backup",
        "mass_editing",
    ],
    'description': 'Install all modules which is related to MTBL OGL System',
    'installable': True,
    'application': True,
}
