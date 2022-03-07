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
        'base',
        'account',
        'operating_unit',
        'mtbl_access',
    ],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu_view.xml',
        'views/res_tpm_product_view.xml',
        'views/tpm_product_change_request_view.xml',
        'views/res_tpm_config_settings_views.xml',
        'views/res_tpm_view.xml',
    ],
    'installable': True,
    'application': True,
}
