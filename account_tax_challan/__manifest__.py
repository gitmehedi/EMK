# -*- coding: utf-8 -*-
{
    'name': "Account Tax Challan",
    'description': """
        Module is responsible for 'TDS & Vat Challan'.This module included with-
        --Selection wizard
        --List of all pending TDS & VAT challan.
        --Generate records For deposite and distribute.
        """,
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting & Finance',
    'depends': [
        'account',
        'l10n_bd_account_tax',
        'account_operating_unit',
    ],
    'data': [
        'security/ir_security.xml',
        'security/ir.model.access.csv',
        'data/tds_vat_challan_data.xml',
        'views/menu_view.xml',
        'wizards/tds_vat_move_payment_wizard.xml',
        'wizards/tds_challan_selection_wizard.xml',
        'wizards/multi_challan_confirm_wizard.xml',
        'wizards/multi_challan_approve_wizard.xml',
        'views/tds_account_move_line_view.xml',
        'views/tds_vat_challan.xml',
        'views/account_config.xml',
        'views/tds_vat_payments.xml',
        'reports/tds_vat_challan_report.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'application': False,
}
