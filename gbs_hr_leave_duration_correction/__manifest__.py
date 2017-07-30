{
    'name': 'HR Leave Days Duration Correction',
    'version': '1.0',
    'category': 'leave',
    'sequence': 30,
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This modules removes datetime from date_from and date_to fields and adds only date",
    'depends': [
        'hr_holidays',
        'gbs_hr_package',
    ],
    'data': [
        'security/hr_holidays_security.xml',
        'views/hr_holidays_view.xml',
    ],
    'installable': True,
    'application': True,
}
