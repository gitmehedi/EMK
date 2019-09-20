{
    'name': 'HR Short Leaves',
    'version': '1',
    'author': 'Genweb2 Limited',
    'category': 'Leave',
    'sequence': 26,
    'summary': 'Hourly Short Leave for Employee(s)',
    'website': 'https://www.genweb2.com',

    'depends': [
        'hr_holidays',
        'hr',
        'calendar',
        'resource',
        'hr_manual_attendance',
        'report',
        'gbs_application_group',
        'hr_holidays_multi_levels_approval',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_short_leave_views.xml',

    ],
    'summary': 'This module handles request of short leave',
    'description':"Complete HR Short Leaves Program",
    'installable': True,
    'application': True,
}