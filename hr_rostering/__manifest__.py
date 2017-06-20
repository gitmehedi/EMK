{
    'name': 'HR Rostering',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Human Resources',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'security/alter.xml',
        'views/hr_shifting.xml',
        'views/hr_shifting_history.xml',
        'views/hr_shift_alter_view.xml',
    ],
    'depends': [
        'hr',
        'hr_payroll',
        'resource',
    ],    
    
    'description': 
    "This module enables employee rostering",        
    'installable': True,
    'application': True,
}