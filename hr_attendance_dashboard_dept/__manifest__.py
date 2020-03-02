{
    'name': 'Attendance Dashboard By Department',
    'author':  'Genweb2 Limited',
    'category': 'Dashboard',
    'version': '0.1',
    'website': 'www.genweb2.com',
    'depends': ['hr_attendance',
                'gbs_hr_attendance',
                'gbs_hr_attendance_utility',
                ],
    'data': [
        'views/hr_attendance_dashboard_view.xml',
        'views/inherited_att_employee_list_view.xml',
        'views/menu.xml',
        # 'security/ir.model.access.csv',
    ],

    'description': '''This module help user to see attendance records by the dashboard''',
    'application': False,
    'installable': True,

}