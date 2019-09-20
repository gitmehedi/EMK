{
    'name': 'Holiday Utility',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'leave',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_holidays_import_view.xml',
        'wizards/hr_holidays_import_wizard_view.xml',
    ],
    
    'depends': [
        'hr_attendance',
        'hr_holidays',
    ],
  
    'installable': True,
    'application': True,
}