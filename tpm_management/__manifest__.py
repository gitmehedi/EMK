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
        'mtbl_access',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu_view.xml',
        'views/account_config_view.xml',
        'views/account_app_config_view.xml',
        'views/tpm_calculation_view.xml'
    ],
    'installable': True,
    'application': True,
}
