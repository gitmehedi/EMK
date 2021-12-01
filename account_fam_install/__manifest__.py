{
    'name': 'Fixed Assets Management Installation',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Accounting Assets',
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
    ],
    'installable': True,
    'application': True,
}
