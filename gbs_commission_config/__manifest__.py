{
    'name': 'Commission & Refund Configuration',
    'version': '10.0.3.3',
    'category': 'Sales',
    'summary': '',
    "description": """
    
    """,
    'author': 'Genweb2 Limited',
    'website': '',
    'depends': ['base', 'gbs_application_group', 'functional_unit', 'customer_business_type'],
    'data': [
        'security/ir.model.access.csv',
        'views/commission_configuration_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
