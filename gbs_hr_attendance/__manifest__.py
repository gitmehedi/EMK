{
    'name': 'GBS HR Attendance',
    'version': '1.0.0',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'category': 'Human Resources',
    'summary': 'This module handles request of HR Attendance',
    'description':"Complete HR Attendance Program",
    'depends': ['hr',
                'hr_attendance',
                'gbs_hr_package',
                ],
    'data': [
        'views/hr_attendance_view.xml',
        'views/hr_emp_map_to_device.xml',
        'security/ir_rule.xml',
    ],
    'installable': True,
    'application': False,
}
