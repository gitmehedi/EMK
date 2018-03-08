{
    'name': 'Delivery Invoicing',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version':'10.1.1.1',
    'depends': [
        'stock',
        'sale',
    ],

    'data': [
        'views/inherit_stock_picking_view.xml',
    ],

    'summary': 'Delivery Invoicing',
    'installable': True,
    'application': False,
}