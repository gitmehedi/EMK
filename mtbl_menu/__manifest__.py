{
    'name': 'MTBL Menu',
    'author': 'Genweb2 Limited',
    'version': '10.0.1.0.0',
    'category': 'base',
    "sequence": 10,
    'summary': 'MTBL Menu Refactor',
    'description': """
This application is to modify the Menu Items.
""",
    'depends': [
        'base',
        'account',
        'account_mtbl',
        'gbs_payment_instruction'
    ],
    'data': [
        'views/inherit_vendor_advance_view.xml',
        'views/inherit_vendor_security_deposit_view.xml',
        'views/inherit_vendor_security_return_view.xml',
        'views/inherit_rent_agreement_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}