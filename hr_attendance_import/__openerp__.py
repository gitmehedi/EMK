{
    'name': 'HR Attendance Import',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [       
       'views/hr_earned_leave_view.xml',
       'wizards/hr_earned_leave_encashment_wizard_views.xml',
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