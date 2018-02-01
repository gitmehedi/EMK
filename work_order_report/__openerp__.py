{
    'name': 'Purchase Order Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'version': '1.0',
    'category': 'Reports',
    'description': """Create work order report""",
    'depends': [
        'purchase',
        'report',
        'amount_to_word_bd',

    ],
    'data': [
        'report/work_order_report_view.xml',
    ],
    'installable': True,
    'application': True,
}
