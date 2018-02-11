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
        'gbs_hr_employee_seniority',
        'gbs_hr_department_sequence',
        'gbs_hr_calendar',
        'gbs_hr_employee_sequence',
        'hr_employee_loan_payroll',
        'custom_report'
    ],
    'data': [
        #'report/report_paperformat.xml',
        'report/gbs_hr_payroll_top_sheet_report.xml',
        'report/payroll_top_sheet_report_view.xml',

    ],
    'summary': 'Shows job titles and payslip reports',
    'description':
        "This module shows job titles when searching employee name, also enables HR Manager to print individual payslip PDF report ",
    'installable': True,
    'application': True,
}
