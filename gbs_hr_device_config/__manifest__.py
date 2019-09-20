{
    'name': 'HR Device Config',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
        'data/ir_cron.xml',
        'views/device_configuration_view.xml',
        'security/ir.model.access.csv',
        'wizard/success_msg.xml',
    ],
    'depends': [
        'hr',
        'hr_attendance',
        'hr_attendance_import',
        "operating_unit",
        "gbs_hr_attendance_utility",
        "gbs_hr_attendance",
        "hr_attendance_settings",
        "hr_attendance_settings",
    ],
    'description': 
    """This module will connect to attendance devices""",
    'installable': True,
    'application': True,
}