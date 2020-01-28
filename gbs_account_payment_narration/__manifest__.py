{
    'name': 'Account Payment Narration',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Account',
    'version': '10.1.1.1',
    'depends': [
        'account_operating_unit',
        'gbs_collection_batch',
        'gbs_vendor_payment',
    ],
    'data': [
        'views/inherited_account_payment_view.xml',
    ],

    'summary': 'Add the narration field on Customer Collection, Customer Collection Batch and Vendor Payment page.',
    'description': """Account Payment Narration""",
    'installable': True,
    'application': False,
}