{
    'name': 'HR Leave Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'version': '1.0',
    'data': [
        'wizard/hr_holidays_summary_department_views.xml',
        'wizard/hr_employee_leave_summary.xml',
        'report/leave_summary_report.xml',

    ],
    'website': 'www.genweb2.com',
    'version': '1.0',
    'data': [
        'wizard/hr_holidays_summary_department_views.xml',
        'wizard/hr_employee_leave_summary.xml',
        'report/leave_summary_report.xml',
    ],
    'depends': [
        'hr_holidays',
        'report',
        'custom_report',
    ],
    'description': """This module enables HR Manager to generate leave related reports in PDF format""",
    'installable': True,
    'application': True,
}
