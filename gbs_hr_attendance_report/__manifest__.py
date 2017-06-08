{
    'name': 'GBS HR Attendance Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'attendance',
    'version': '1.0',
    'depends': [
        'hr_attendance', 'hr', 'gbs_hr_calendar',
    ],
    'data': [
        'report/gbs_hr_attendance_report.xml',
        'report/gbs_hr_attendance_duration_report.xml',
        'wizard/hr_attendance_report_wizard_views.xml',
        'wizard/hr_attendance_duration_wizard_views.xml',
    ],

    'summary': 'Generates check in and check out related report of employee(s)',
    'description': 'Generates check in and check out related report of employee(s)',
    'installable': True,
    'application': True,
}
