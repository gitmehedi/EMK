{
    'name': 'HR Leave Days Duration Correction',
    'version': '10.0.1.0.0',
    'category': 'leave',
    'sequence': 30,
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This modules removes datetime from date_from and date_to fields and adds only date",
    'description':"Complete HR Leave Days Duration Correction Program",
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_view.xml',
    ],
    'installable': True,
    'application': True,
}
