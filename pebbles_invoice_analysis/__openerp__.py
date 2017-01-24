# -*- coding: utf-8 -*-
##############################################################################
{
    'name' : 'PEBBLES INVOICE ANALYSIS',
    'version' : '1.0',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category' : 'Accounting & Finance',
    'description' : """
    Pebbles Invoice Analysis
    ====================================
    """,
    'depends' : ['base_setup', 'product', 'analytic', 'board', 'edi', 'report','account'],
    'data': [
        # 'security/account_security.xml',
        # 'security/ir.model.access.csv',
        'report/pebbles_account_invoice_report_view.xml',
        'wizard/pebbles_account_invoice_wizard_view.xml',
        # 'report/account_report_view.xml',
        # 'report/account_analytic_entries_report_view.xml',
        # 'wizard/account_move_bank_reconcile_view.xml',
        # 'wizard/account_use_model_view.xml',
        # 'account_installer.xml',
        # 'wizard/account_period_close_view.xml',
        # 'wizard/account_reconcile_view.xml',
        # 'wizard/account_unreconcile_view.xml',
        # 'wizard/account_statement_from_invoice_view.xml',
        # 'account_view.xml',
        # 'account_report.xml',
        # 'account_financial_report_data.xml',
        # 'wizard/account_report_common_view.xml',
        # 'project/wizard/project_account_analytic_line_view.xml',
        # 'account_end_fy.xml',
        # 'account_invoice_view.xml',
        # 'data/account_data.xml',
        # 'data/data_account_type.xml',
        # 'data/configurable_account_chart.xml',

    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
