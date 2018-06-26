{
    'name': 'Samuda Sale Order Type',
    'version': '10.1.0.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "Introducing various Samuda Sale Order types.",
    'depends': [
        'gbs_application_group',
        'operating_unit',
        'sale_order_type',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/inherited_sale_order_type_view.xml',
    ],
    'installable': True,
    'application': False,
}
