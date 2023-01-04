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
        'security/ir.model.access.csv',
        'data/branch_data.xml',
        'views/res_branch_view.xml',
        'views/inherited_res_company.xml',
        'views/inherited_stock_picking.xml',
        'views/inherited_stock_move.xml',
        'views/inherited_product.xml',
        'views/inherited_partner.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
