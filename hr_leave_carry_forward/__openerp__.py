{
    'name': 'HR Leave Carry Forward',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Leave Carry Forward',
    'version':'1.0',
    'data': [
        'wizards/hr_leave_carry_forward_wizard_views.xml',
        'views/hr_leave_carry_forward_view.xml'   
    ],
    'depends': [
        'hr',
        'hr_holidays',
        ],
    'summary': 'Leave carry forward process is calculated ',
    'description': 
    """This module gives opportunity to decide user either he wants to carry forward his/her leaves
            leave ot not'""",        
    'installable': True,
    'application': True,
}