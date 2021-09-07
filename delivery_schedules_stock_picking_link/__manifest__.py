{
    'name': 'Delivery Schedules Stock Picking Link',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version': '10.0.1.0.0',
    'depends': [
        'delivery_schedules',
        'delivery_order'
    ],
    'data': [
        'wizards/message_box_view.xml',
        'views/delivery_schedules_view.xml',
        'views/stock_picking_view.xml'
    ],
    'summary': 'Adds link between delivery schedules and stock pickings',
    'description': 'Adds link between delivery schedules and stock pickings',
    'installable': True,
    'application': False
}
