{
    'name': 'Bangla Payslip',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Payroll',
    'version': '10.0.1.0.0',
    'depends': [
        'hr_payroll',
        'report_xlsx',
        ],
    'data': [
        'views/inherited_hr_payslip_view.xml',
        'reports/payslip_bangla_report.xml',

    ],
    "external_dependencies": {
        'python': ['bangla'],
    },


    'installable': True,
    'application': False,
}