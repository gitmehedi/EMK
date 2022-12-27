{
    'name': 'Functional Unit',
    'version': '10.0.3.3',
    'category': 'Sales',
    'summary': 'Multiple Functional Unit Operation on Sales,Purchases,Accounting/Invoicing,Voucher,Paymemt,POS, '
               'Accounting Reports for single company',
    "description": """
    
    """,
    'author': 'Genweb2 Limited',
    'website': '',
    'depends': ['base', 'stock', 'account', 'web'],
    'data': [
        'security/branch_security.xml',
        'security/ir.model.access.csv',

        'data/branch_data.xml',

        'views/res_branch_view.xml',
        'views/inherited_res_users.xml',
        'views/inherited_stock_picking.xml',
        'views/inherited_stock_move.xml',
        'views/inherited_account_invoice.xml',
        'views/inherited_stock_warehouse.xml',
        'views/inherited_stock_location.xml',
        'views/inherited_account_bank_statement.xml',
        'wizard/inherited_account_payment.xml',
        'views/inherited_stock_inventory.xml',
        'views/inherited_product.xml',
        'views/inherited_partner.xml',
        'views/inherited_res_company.xml'
    ],
    'qweb': [
        'static/src/xml/branch.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images": ['static/description/Banner.png'],
    'post_init_hook': 'post_init_hook',
}
