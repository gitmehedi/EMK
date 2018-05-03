{
    'name': 'Sale By LC',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'10.0.1.0.0',
    'depends': [
        'letter_of_credit',
    ],

    'data': [
        'wizard/lc_wizard_view.xml',
        'views/lc_sales_view.xml',
        'views/lc_sales_menu.xml',
    ],

    'summary': 'Sale By LC',
    'installable': True,
    'application': False,
}