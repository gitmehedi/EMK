# -*- coding: utf-8 -*-
{
    'name': "GBS HR Payroll Cost Center wise Topsheet",

    'summary': """""",

    'description': """
    """,

    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',

    'category': 'payroll',
    'version': '10.0.0.0.1',

    'depends': ['base', 'report_xlsx', 'report', 'account_cost_center', 'gbs_hr_payroll',
                'gbs_employee_cost_center_link'],

    'data': [
        'wizards/cost_center_top_sheet_view.xml',
        'reports/cost_center_wise_top_sheet_xlsx_view.xml',
    ],
}
