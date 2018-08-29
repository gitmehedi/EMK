{
    'name': 'Accounts Integration to Sales Commission',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'accounts',
    'depends': [
        'gbs_account',
        'product',
        'account',
        'gbs_sales_commission',
    ],

    'data': [
        'views/inherit_product_template_view.xml',

    ],

    'description': 'Accounts Integration to Sales Commission',
    'installable': True,
    'application': False,
}