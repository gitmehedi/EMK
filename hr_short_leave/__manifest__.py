{
    'name': 'Short Leaves',
    'version': '1',
    'category': 'Leave',
    'sequence': 27,
    'summary': 'Short Leave',
    'website': 'https://www.genweb2.com',

    'depends': [
        'hr_holidays'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_short_leave_views.xml',
    ],

    'installable': True,
    'application': True,
}
