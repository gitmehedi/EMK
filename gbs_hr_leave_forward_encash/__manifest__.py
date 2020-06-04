{
    'name': 'HR Leave Carry Forward and Encashment For Samuda',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Leave Carry Forward',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'security/hr_leave_forward_encash_security.xml',
        'wizards/hr_leave_carry_forward_wizard_views.xml',
        'wizards/my_leave_confirm_wizard_view.xml',
        'views/hr_leave_forward_encash_view.xml',
        'views/inherited_hr_forward_encash_view.xml',
        'views/hr_my_leave_forward_encash_view.xml',
        
    ],
    'depends': [
        'hr',
        'hr_holidays',
        'hr_attendance',
        'gbs_hr_attendance',
        'hr_employee_seniority',
        'hr_holiday_year',
        ],
    'summary': 'Leave carry forward and encashment process is calculated ',
    'description': 
    """This module gives opportunity to decide user either he wants to carry forward his/her leaves
            leave or not and also how many leaves will encashment '""",
    'installable': True,
    'application': True,
}