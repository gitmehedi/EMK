{
    'name': 'GBS HR Employee',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'payroll',
    'version': '10.0.1.0.0',
    'depends': [
        'hr','hr_employee_seniority'
    ],
    'data': [
        "views/hr_emp_tin_view.xml",
        "views/hr_emplyee_sequence.xml",
    ],
    'summary': 'Shows job titles and employee tin informations ',
    'description':
        "This module shows job titles when searching employee name",
    'installable': True,
    'application': True,
}
