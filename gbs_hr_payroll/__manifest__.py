{
    'name': 'GBS HR Payroll',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'payroll',
    'version': '10.0.1.0.0',
    'depends': [
        'hr',
        'hr_payroll', 
        'l10n_in_hr_payroll',
        'hr_employee_seniority',
        'gbs_hr_department_sequence',
        # 'gbs_hr_calendar',
        'gbs_hr_employee',
        'gbs_hr_employee_sequence',
        'hr_employee_loan_payroll',
        'custom_report',
        'amount_to_word_bd'
    ],
    'data': [
        'wizard/inherited_hr_payroll_payslips_by_employees_views.xml',
        'report/payroll_report_view.xml',
        'report/report_payrolladvice_inherit.xml',
        'views/hr_contract_view.xml',
        'views/inherited_hr_payslip_run_views.xml',
        'views/hr_payslip.xml',
        "views/inherit_res_partner_bank_view.xml",
    ],
    'summary': 'Shows payslip reports',
    'description':
        "This module shows HR Manager to print individual payslip PDF report ",
    'installable': True,
    'application': True,
}
