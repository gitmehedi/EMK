{
    'name': 'Samuda Custom Letter of Credit',
    'version': '10.1.0.0',
    'category': 'Commercial',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "Samuda Custom Letter of Credit Adviser Permission",
    'depends': [
        'commercial',
        'letter_of_credit',
        'lc_sales_product_local',
    ],

    'data': [
        'security/security.xml',
        'views/inherited_letter_credit_views.xml'

    ],
    'installable': True,
    'application': True,
}
