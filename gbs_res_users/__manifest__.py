{
    'name': 'GBS USERS',
    'version': '10.0.1',
    'author': 'Genweb2 Limited',
    'website': 'https://www.genweb2.com',

    'depends': [
        'base',
        'stock',
    ],

    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/res_users_view.xml',
    ],
    'summary': 'This module handles custom ir sequence',
    'description':"Complete Solution for operating unit wise sequence",
    'installable': True,
    'application': True,
}