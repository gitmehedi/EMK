{
    'name': 'HR Payroll Overtime',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Payroll',
    'version': '10.0.1.0.0',
    'depends': [
        'hr_payroll',
        'hr_employee_attendance_payroll',
        'report_xlsx',
        ],
    'data': [
        'data/data.xml',
        'reports/ot_report_view.xml',
        'reports/top_sheet_department_view.xml',
        'wizard/ot_report_wizard.xml',
        'views/hr_payslip_run_view.xml',
    ],

    'summary': 'This Module Generate Payroll overtime Summary',

    'installable': True,
    'application': False,
}