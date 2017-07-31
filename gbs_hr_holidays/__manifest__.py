{
    'name': 'GBS HR Holiday',
    'version': '1.0.0',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'category': 'Human Resources',
    
    'depends': ['hr',
                'hr_holidays',
                'gbs_hr_package',
                'hr_public_holidays'
                ],
    'data': [
        'security/ir_rule.xml',
        'views/hr_holidays_view.xml',
    ],
    'installable': True,
    'application': False,
}
