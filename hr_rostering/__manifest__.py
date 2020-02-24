{
    'name': 'HR Rostering',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Human Resources',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'security/alter.xml',
        'security/shifting_rule.xml',
        'wizard/hr_shift_employee_batch_wizard_views.xml',
        'views/hr_shifting.xml',
        'views/hr_shifting_history.xml',
        'views/hr_shift_alter_view.xml',
        'views/hr_shift_employee_batch_views.xml',
        'views/hr_shift_alter_batch.xml'
    ],
    'depends': [
        'hr',
        'resource',
        'operating_unit',
        'hr_employee_operating_unit',
        'gbs_hr_package',
        'hr_holidays_multi_levels_approval',
    ],    
    
    'description': 
    "This module enables employee rostering",        
    'installable': True,
    'application': True,
}
