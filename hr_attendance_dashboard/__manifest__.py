{
    'name': 'Employee Attendance Dashboard',
    'author':  'Genweb2 Limited',
    'category': 'Dashboard',
    'version': '0.1',
    'website': 'www.genweb2.com',
    'data': [
        'views/hr_attendance_dashboard_view.xml',
        'security/ir.model.access.csv',
    ],
    'depends': ['hr','hr_employee_operating_unit'],
    'description': '''This module help user to see attendance records by the dashboard''',
    'application': False,
    'installable': True,

}