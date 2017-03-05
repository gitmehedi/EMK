{
    'name': 'HR Attendance Import',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [       
       'security/security.xml',
       'security/ir.model.access.csv',
       'views/hr_attendance_import_view.xml',
       'wizards/hr_attendance_import_wizard_view.xml',
    ],
    
    'depends': [
        'hr_attendance', 
        'hr', 
        'hr_holidays', 
       
    ],    
    
    'description': """This module enables HR Manager to import attendance data""",        
  
    'installable': True,
    'application': True,
}