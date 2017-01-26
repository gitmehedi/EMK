{
    'name': 'HR Manual Attendance Request',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'views/hr_manual_attendance_view.xml',
        #'views/inherited_hr_holidays_status_data.xml',
        'security/hr_manual_attendance_security.xml',
       
    ],
    
    'depends': [
        'hr_attendance',
        'hr',
        'hr_holidays',        
        ],    
    
    'description': 
    """This module enables employee to request manual attendance""",        
    'installable': True,
    'application': True,
}