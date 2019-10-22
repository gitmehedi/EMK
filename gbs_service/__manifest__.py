{
    'name': 'GBS Service',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Services',
    'version': '10.0.0.1',
    'depends': [
        'gbs_product',
        'gbs_purchase_requisition',
    ],
    'data': [
        'views/inherited_product_template_view.xml',
        'views/menu_items.xml',
    ],
    'summary': "Services",
    'description': "services for charges of lc collection",
    'installable': True,
    'application': False,
}