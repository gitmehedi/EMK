{
    'name': 'HR Holiday Exception',
    'version': '10.0.1.0.0',
    'sequence': 30,
    'category': 'Human Resources',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "Manage Holiday exception",
    'description':"""
        By this module employee can get exceptional leave.
        If an employee work in holiday then they can get alter compensatory leave
        or OT. 
    """,
    'depends': [
        'gbs_hr_public_holidays',
        'hr_rostering',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizard/hr_holiday_exception_wizard_view.xml',
        'views/hr_holiday_exception_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
