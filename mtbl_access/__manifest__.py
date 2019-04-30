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
        'portal',
        'account',
        'account_fiscal_year',
        'account_type_menu',
        'account_parent',
        'date_range',
        'account_mtbl',
        'operating_unit',
        'sub_operating_unit',
    ],
    'data': [
        'security/ir_security.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/menuitems.xml',
        'views/report_view_access.xml',
        'views/act_window_access.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}