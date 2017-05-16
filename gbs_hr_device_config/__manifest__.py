{
    'name': 'HR Device Config',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
       'views/device_configuration_view.xml',
    ],
    'depends': [
        'hr_attendance_and_ot_summary',

    ],
    'description': 
    """This module will connect to attendance devices""",
    'installable': True,
    'application': True,
}