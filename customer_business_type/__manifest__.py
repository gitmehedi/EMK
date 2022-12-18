{
    'name': 'Customer Business Type',
    'version': '10.0.3.3',
    'category': 'Sales',
    'summary': '',
    "description": """
    
    """,
    'author': 'Genweb2 Limited',
    'website': '',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_customer_type_view.xml',
        'views/inherited_partner.xml',
        'views/inherited_res_company_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
