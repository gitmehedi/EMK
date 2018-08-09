{
    'name': 'Delivery Challan Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'sales',
    'version':'1.1.1',
    'depends': [
        'stock',
    ],

    'data': [
        'reports/delivery_challan_report_view.xml',
        'reports/inherit_stock_picking_report.xml',
    ],

    'summary': 'Reports printing for Delivery Challan',
    'installable': True,
    'application': False,
}