{
    'name': 'HR Leave Encashment',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Leave Encashment',
    'version':'1.0',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/hr_earned_leave_encashment_wizard_views.xml',
        'views/hr_earned_leave_view.xml',
        'views/inherited_hr_earned_leave_view_.xml',    
    ],
    'depends': [
        'hr',
        'hr_holidays',
        ],
    'summary': 'Earned leave encashment process is calculated(Not Sure What are the purpose of this module) ',
    'description': 
    """This module gives opportunity to decide user either he wants to encash his/her earned 
            leave ot not'""",        
    'installable': True,
    'application': True,
}