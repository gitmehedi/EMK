{
    'name': 'GBS HR Attendance Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'attendance',
    'version': '1.0',
    'depends': [
        'hr_attendance',
        'hr',
        'gbs_hr_calendar',
        'gbs_hr_employee_sequence',
        'hr_employee_operating_unit'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'report/report_paperformat.xml',
        'report/gbs_hr_attendance_report.xml',
        'wizard/hr_attendance_duration_wizard_views.xml',
        'report/gbs_hr_attendance_duration_report.xml',
        #'report/daily_attendance_report.xml',
        #'report/daily_attendance_report_templates.xml',
        'report/hr_daily_attendance_report_template.xml',
        'wizard/hr_attendance_report_wizard_views.xml',
        #'wizard/daily_attendance_report_wizard_view.xml',
        'wizard/hr_daily_attendance_report_wizard_views.xml',
        'report/gbs_hr_attendance_report_template.xml',
    ],

    'summary': 'Generates check in and check out related report of employee(s)',
    'description': 'Generates check in and check out related report of employee(s)',
    'installable': True,
    'application': True,
}
