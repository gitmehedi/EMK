{
    'name': 'Employee Roster View',
    'version': '10.0.1',
    'category': 'Human Resources',
    'sequence': 101,
    'summary': 'Employee Roster View',
    'description': "",
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'depends': [
        'base',
        'base_setup',
        'hr',
        'hr_rostering',
    ],
    'data': [
        'views/hr_attendance_settings_views.xml',
        'views/lib.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
