{
    'name': 'Print Journal Items',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'This module allow user to print journal items in PDF format.',
    'description': """ This module allow user to print journal items in PDF format.""",
    'author': 'Genweb2 Ltd',
    'website': 'www.genweb2.com',
    'depends': [
        'account',
        'custom_report',
    ],

    'data': [
        'view/journal_items_view.xml'
    ],

    'installable': True,
    'application': False,
}
