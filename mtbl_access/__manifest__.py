{
    'name': 'MTBL Access Rights',
    'author': 'Genweb2',
    'version': '10.0.1.0.0',
    'category': 'base',
    "sequence": 10,
    'summary': 'All Access Rights of mtbl',
    'description': """
Manage the recruitment access rights
================================================

This application allows you to easily maintain access rights of mtbl process.
""",
    'depends': [
        'base',
        'account_mtbl'

    ],
    'data': [
        'security/ir_security.xml',
        'security/ir.model.access.csv',
        'views/menuitems.xml'


    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}