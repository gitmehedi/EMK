{
    'name': 'Custom Currency Conversion',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'account',
    # 'sequence': 101,
    'version': '10.1.1.1',
    'depends': [
        'base',
        'account',
        'purchase',
        'gbs_collection_batch',
        'gbs_collection_letter_of_credit'
    ],

    'data': [
        'views/inherit_account_invoice_view.xml',
        'views/inherit_account_payment_view.xml',
        'views/inherit_account_payment_batch_view.xml',
    ],

    'summary': 'Convert foreign currencies on a given conversion rate',
    'installable': True,
    'application': False,
}