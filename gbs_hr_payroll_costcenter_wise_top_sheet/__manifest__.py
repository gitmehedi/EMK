# -*- coding: utf-8 -*-
{
    'name': "GBS HR Payroll Cost Center wise Topsheet",

    'summary': """""",

    'description': """
    """,

    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_xlsx', 'report', 'account_cost_center','gbs_hr_payroll','gbs_employee_cost_center_link'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/cost_center_top_sheet_view.xml',
        'reports/cost_center_wise_top_sheet_xlsx_view.xml',
    ],
}
