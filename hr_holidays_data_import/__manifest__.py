{
    'name': 'Leave Holidays Data Import',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'leave',
    'version':'1.0',
    'data': [
       'views/hr_holidays_import_view.xml',
       'wizards/hr_holidays_import_wizard_view.xml',
    ],
    
    'depends': [
        'hr_attendance',
    ],
  
    'installable': True,
    'application': True,
}