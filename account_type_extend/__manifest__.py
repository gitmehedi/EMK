{
    'name': 'Account Type Extend',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting',
    'depends': [
        'account',
        'account_operating_unit',
        'account_department_dimension',
        'account_cost_center'
    ],
    'data': [
        'views/account_type_view.xml',
        'views/account_move_view.xml'
    ],
    'description': 'This module adds required or optional feature for some fields of '
                   'journal entries based on account type of an account.',
    'installable': True,
    'application': False,
}
