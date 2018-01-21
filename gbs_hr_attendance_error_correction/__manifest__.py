{
    'name': 'HR Attendance Error Correction',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
        'wizards/hr_attendance_error_wizard_view.xml',
        'views/hr_attendance_error_view.xml'
    ],
    'depends': [
        'hr',
        'hr_attendance',
        'gbs_hr_attendance',
        ],
    'summary': 'HR attendance error data correction process.',
    'description':
    """This module provides the way to correct the error of attendance data.""",
    'installable': True,
    'application': True,
}