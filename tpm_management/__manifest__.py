{
    'name': 'Transfer Pricing Mechanism (TPM)',
    'author': 'Genweb2 Limited',
    'website': 'https://www.genweb2.com',
    'version': '10.0.1.0.0',
    'category': 'account',
    "sequence": 10,
    'summary': 'Transfer Pricing Mechanism',
    'description': """
Transfer Pricing Mechanism.
""",
    'depends': [
        'account',
        'operating_unit',
    ],
    'data': [
        # 'security/ir_security.xml'
        'views/account_config.xml'
    ],
    'installable': True,
    'application': True,
}
