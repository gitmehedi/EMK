{
    'name': 'Employee Criteria',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'This module maintain employee criteria',
    'description': """
Periodical Employees Criteria
==============================================

    """,
    'author': "Genweb2",
    'website': "http://www.genweb2.com",
    'depends': [
        'hr',
        'gbs_application_group',
        'gbs_purchase_requisition',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/hr_evaluation_criteria.xml',

    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
