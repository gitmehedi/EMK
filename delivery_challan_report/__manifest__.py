{
    'name': 'Delivery Challan Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'sales',
    'version':'1.1.1',
    'depends': [
        'stock',
        'custom_report',

    ],

    'data': [
        'reports/delivery_challan_potro_report_view.xml',
    ],

    'summary': 'Reports printing for Delivery Challan and Challan Potro',
    'installable': True,
    'application': False,
}