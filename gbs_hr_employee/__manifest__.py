{
    'name': 'GBS HR Employee',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Human Resources',
    'version': '10.0.1.0.0',
    'depends': [
        'hr',
        'base_suspend_security',
	'hr_contract',
	'hr_recruitment'
    ],
    'data': [

        "views/hr_employee_view.xml",
        "views/hr_job_view.xml",

    ],
    'summary': 'Shows job titles and employee tin informations ',
    'description':
        "This module shows job titles when searching employee name",
    'installable': True,
    'application': False,
}
