{
    'name': 'Users tracker',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'base',
    'version':'10.0.1',
    'depends': [
        'base',
        'mail',
        'base_user_role'
    ],
    'data': [
        'views/res_user_inherited_views.xml',
    ],

    'description':
    "This module is tracking all users activity",
    'installable': True,
    'application': True,
}