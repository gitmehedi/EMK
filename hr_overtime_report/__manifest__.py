{
    'name': 'GBS HR Overtime Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'attendance',
    'version': '10.0.1.0.0',
    'depends': [
        'hr_attendance',
        'hr',
        'gbs_hr_calendar',
        'gbs_operating_unit',
        'gbs_hr_employee',
        'hr_employee_operating_unit',
        'gbs_hr_attendance_utility',
        'gbs_hr_device_config',
        'report_layout',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/hr_employee_overtime_summary.xml',
        'reports/overtime_summary_report.xml',
    ],

    'summary': 'Generates overtime report of employee(s)',
    'description': 'Generates overtime report of employee(s)',
    'installable': True,
    'application': True,
}
