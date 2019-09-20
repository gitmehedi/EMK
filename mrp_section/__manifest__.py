{
    'name': "MRP SECTION",
    'author': 'Genweb2',
    'version': '10.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'MRP Section Process',
    'description': "Manage mrp section process",

    'depends': [
        'mrp',
        'base',
        'operating_unit',
    ],
    'data': [
        #'security/ir.model.access.csv',
        'views/mrp_section_view.xml',
        'views/mrp_section_users_views.xml',
    ],
    'installable': True,
    'application': False,
}