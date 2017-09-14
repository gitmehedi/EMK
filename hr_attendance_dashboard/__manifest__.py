{
    'name': 'Employee Attendance Dashboard',
    'author':  'Genweb2 Limited',
    'category': 'Dashboard',
    'version': '0.1',
    'website': 'www.genweb2.com',
    'data': [
        'views/hr_attendance_dashboard_view.xml',
        'views/inherited_att_employee_list_view.xml',
        'security/ir.model.access.csv',
    ],
    'depends': ['hr','hr_employee_operating_unit','gbs_hr_attendance_error_correction'],
    'description': '''This module help user to see attendance records by the dashboard''',
    'application': False,
    'installable': True,

}