{
    'name': 'GBS HR Payroll',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'payroll',
    'version': '1.0',
    'depends': [
        'hr',
        'hr_payroll', 
        'gbs_hr_employee_seniority',
        'gbs_hr_department_sequence',     
                
    ],
    'data': [
        'report/gbs_hr_payroll_report.xml',
        'report/payroll_report_view.xml',
    ],

    'summary': 'Shows job titles and payslip reports',
    'description':
        "This module shows job titles when searching employee name, also enables HR Manager to print individual payslip PDF report ",
    'installable': True,
    'application': True,
}