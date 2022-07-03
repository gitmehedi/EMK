{
    'name': 'Fixed Assets Management Installation',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Install',
    "sequence": 10,
    'summary': 'Install all modules inside FAM functionality',
    'description': """
    Install all modules inside FAM functionality.
    """,
    'depends': [
        'account_fam_access',
        'account_fam',
        'account_fam_category',
        'account_fam_menu',
        'account_fam_vendor_bills',
        'account_vendor_bills',
        'l10n_bd_account_tax',
    ],
    'installable': True,
    'application': True,
}
