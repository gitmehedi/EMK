{
    'name': 'GBS HR Exclude Employee',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'employee',
    'version': '1.0',
    'depends': [
        'hr',
    ],

    'data': [
        'views/hr_exclude_employee_view.xml',
        'security/ir.model.access.csv',
    ],

    'summary': 'Employee Custom list',
    'installable': True,
    'application': True,
}