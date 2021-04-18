{
    'name': 'Database Duplicate and Operations',
    'author': 'Genweb2 Limited',
    'website': 'https://www.genweb2.com',
    'version': '10.0.1.0.0',
    'category': 'account',
    "sequence": 10,
    'summary': 'Database Duplicate and Operations',
    'description': """
        Database Duplicate and Operations
    """,
    'depends': [
        'mtbl_access',
        'gbs_ogl_cbs_interface',
    ],
    'data': [
        'views/menu_view.xml',
        'views/db_operations_view.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': True,
}
