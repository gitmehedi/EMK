{
    "name": "GBS HR Attendance Grace Time",
    "summary": """""",
    "version": "1.0.0",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": [
        'hr',
        'hr_attendance',
        'hr_employee_operating_unit'
    ],
    "data": [
        "views/hr_attendance_grace_time_views.xml",
        "security/ir_rule.xml",
    ],
    'installable': True,
    'application': True
}
