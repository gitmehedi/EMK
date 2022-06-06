{
    'name': 'HR Holiday Year',
    'version': '10.0.2',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'category': 'Human Resources',
    'summary': """Computes the actual leave days 
               considering rest days and public holidays""",
    'depends': [
        'hr_holidays',
        'date_range',
    ],
    'data': [
        'views/menu_view.xml',
        'views/hr_holidays_view.xml',
        'views/date_range_view.xml',
    ],
    'installable': True,
    'application': True,
}
