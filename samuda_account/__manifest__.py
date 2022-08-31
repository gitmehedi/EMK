{
    'name': 'Samuda Account',
    'version': '10.1.0.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "",
    'depends': [
        'account',
        'samuda_so_type',
        'account_invoice_merge'
    ],

    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_merge_view.xml',
        'views/sale_type_product_acc.xml',
        'views/inherit_invoice_lc_view.xml',
        'views/account_view.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': True,
}
