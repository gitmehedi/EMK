{
    'name': 'HR Leave Carry Forward',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Leave Carry Forward',
    'version':'1.0',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/hr_leave_carry_forward_wizard_views.xml',
        'views/hr_leave_carry_forward_view.xml',
        'views/inherited_hr_carry_forward_view.xml',
        
    ],
    'depends': [
        'hr',
        'hr_holidays',
        'hr_holidays_leave_year',
      #  'hr_earned_leave',
        ],
    'summary': 'Leave carry forward process is calculated(Not Sure What are the purpose of this module) ',
    'description': 
    """This module gives opportunity to decide user either he wants to carry forward his/her leaves
            leave ot not'""",        
    'installable': True,
    'application': True,
}