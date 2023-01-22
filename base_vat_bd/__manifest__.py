{
    'name': 'Drop Customers Trade and VAT license',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting & Finance',
    'depends': [
        'account',
        'mtbl_access',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/inherit_account_tax_wizard_view.xml',
        'views/inherited_res_partner_view.xml',
        'views/inherited_account_tax.xml',
    ],
    'description': 'Customer TAX And VAT Registration Details',
    'installable': True,
    'application': True,
}
