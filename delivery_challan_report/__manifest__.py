{
    'name': 'Delivery Challan Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'sales',
    'version':'1.1.1',
    'depends': [
        'stock',
        'amount_to_word_bd',
        'report_layout',
    ],

    'data': [
        'reports/inherit_stock_picking_report.xml',
        'reports/delivery_challan_reporting_view.xml',
    ],

    'summary': 'Reports printing for Delivery Challan',
    'installable': True,
    'application': False,
}