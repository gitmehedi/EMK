{
    'name': 'Employee Seniority',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Keep Track of Length of Employment
==================================
    """,
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'gbs_hr_security',
        'gbs_hr_employee_sequence',
        
    ],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
        'hr_view.xml',
    ],
    'test': [
    ],
    'installable': True,
}
