{
    'name': 'HR Leave Encashment',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Leave Encashment',
    'version':'1.0',
    'data': [
        'wizards/hr_earned_leave_encashment_wizard_views.xml',
        'views/hr_earned_leave_view.xml'   
    ],
    'depends': [
        'hr',
        'hr_holidays',
        ],
    'summary': 'Earned leave encashment process is calculated ',
    'description': 
    """This module gives opportunity to decide user either he wants to encash his/her earned 
            leave ot not'""",        
    'installable': True,
    'application': True,
}