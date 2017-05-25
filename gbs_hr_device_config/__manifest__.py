{
    'name': 'HR Device Config',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
       'views/device_configuration_view.xml',
        'views/hr_emp_map_to_device.xml',
    ],
    'depends': [
        'hr',
        'hr_attendance',
    ],
    'description': 
    """This module will connect to attendance devices""",
    'installable': True,
    'application': True,
}