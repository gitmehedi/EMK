{
    'name': 'GBS HR Recruitment Access Rights',
    'author': 'Genweb2',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Recruitment Process',
    'description': """
Manage the recruitment access rights
================================================

This application allows you to easily maintain access rights of recruitment process.
""",
    'depends': [
        'gbs_application_group',
        'gbs_base_package',
        'hr_employee_operating_unit',
        # 'gbs_hr_recruitment',
    ],
    'data': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}