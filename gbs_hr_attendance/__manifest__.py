{
    'name': 'GBS HR Attendance',
    'version': '1.0.0',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'category': 'Human Resources',
    
    'depends': ['hr',
                'hr_attendance',
                ],
    'data': [
        # 'views/hr_attendance_view.xml',
        'security/ir_rule.xml',

    ],
    'installable': True,
    'application': False,
}
