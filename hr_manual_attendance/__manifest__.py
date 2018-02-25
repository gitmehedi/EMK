{
    'name': 'HR Manual Attendance Request',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'security/hr_manual_attendance_security.xml',
        'views/hr_manual_attendance_view.xml',
        'views/manual_attendance_min_days_restriction_view.xml',
        'views/hr_manual_attendance_batches_view.xml',

    ],
    
    'depends': [
        'hr_attendance',
        'hr',
        'hr_holidays',
        'gbs_hr_attendance',
        'hr_holidays_multi_levels_approval',
    ],    
    
    'description': 
    """This module enables employee to request manual attendance""",        
    'installable': True,
    'application': True,
}