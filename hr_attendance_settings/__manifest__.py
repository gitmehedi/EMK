{
    'name': 'HR Attendance Settings',
    'version': '10.0.1',
    'category': 'Human Resources',
    'sequence': 101,
    'summary': 'Customized settings for HR Attendance',
    'description': """
HR Attendance Settings
==========================

This application enables you to change the configurable part
You can manage:
---------------
* Attendance Summary
* Attendance Role
    """,
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'depends': [
        'base',
        'base_setup',
        'hr_attendance',
    ],
    'data': [
        'data/settings_data.xml',
        'security/ir.model.access.csv',
        'views/hr_attendance_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
