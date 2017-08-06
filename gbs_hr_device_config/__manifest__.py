{
    'name': 'HR Device Config',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
        'data/ir_cron.xml',
        'views/device_configuration_view.xml',
        'views/hr_emp_map_to_device.xml',
        'security/ir.model.access.csv',
    ],
    'depends': [
        'hr',
        'hr_attendance',
        'hr_attendance_import',
        "operating_unit",
    ],
    'description': 
    """This module will connect to attendance devices""",
    'installable': True,
    'application': True,
}