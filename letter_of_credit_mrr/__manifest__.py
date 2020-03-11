{
    'name': 'GBS Letter Of Credit MRR',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version': '10.1.1.1',
    'depends': [
        'letter_of_credit',
        'stock_picking_extend',
    ],
    'data': [
        'views/inherited_stock_picking_view.xml',
        'views/inherited_letter_of_credit_view.xml',
    ],

    'summary': 'Show MRR button on Import LC page.',
    'description': """GBS Letter Of Credit MRR""",
    'installable': True,
    'application': False,
}