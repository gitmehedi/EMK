{
    'name': 'HR Earned Leave',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Earned Leave',
    'version':'1.0.0',
    'data': [
        'views/hr_earned_leave_view.xml',
        # 'views/inherited_hr_holidays_status_data.xml',
    ],
    'depends': [
        'hr',
        'hr_holidays',
        ],
    'summary': 'Calculates Employees Earned Leave',
    'description': 
    """This module calculates the earned leave of the employee 
        based on the condition of yearly/monthly/Quarterly'""",        
    'installable': True,
    'application': True,
}