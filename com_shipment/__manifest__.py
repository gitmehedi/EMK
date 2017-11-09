{
    'name': 'Shipment',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'1.0.0',
    'depends': [
        'commercial',
        'letter_of_credit',
    ],

    'data': [
            'views/shipment_view.xml',
            'views/shipment_menu.xml',
    ],

    'summary': 'LC Shipment',
    'installable': True,
    'application': False,
}