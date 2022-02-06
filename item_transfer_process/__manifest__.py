{
    'name': "Item Transfer Process",

    'summary': """
            Unit to Unit Item Transfer Process
    
    """,

    'description': """
        Unit to Unit Item Transfer Process
    """,

    'author': 'Genweb2 Limited',

    'category': 'Inventory',
    'version': '10.0.1',

    'depends': ['item_loan_process'],

    'data': [
        'data/sequence.xml',
        'views/item_transfer_send_views.xml',
        'views/item_transfer_receive_views.xml',
        'views/stock_location_view.xml',
        'wizards/confirm_item_receive_view.xml'
    ]
}
