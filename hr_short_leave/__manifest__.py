{
    'name': 'HR Short Leaves',
    'version': '1',
    'author': 'Genweb2 Limited',
    'category': 'Leave',
    'sequence': 26,
    'summary': 'Short Leave',
    'website': 'https://www.genweb2.com',

    'depends': [
        'hr_holidays', 'hr', 'calendar', 'resource', 'product', 'report',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_short_leave_views2.xml',

    ],

    'installable': True,
    'application': True,
}