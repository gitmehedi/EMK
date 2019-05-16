{
    'name': 'MTBL Access Rights',
    'author': 'Genweb2 Limited',
    'version': '10.0.1.0.0',
    'category': 'base',
    "sequence": 10,
    'summary': 'All Access Rights of mtbl',
    'description': """
This application allows you to easily maintain access rights of mtbl process.
""",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir_security.xml',
        # 'security/ir_rule.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
