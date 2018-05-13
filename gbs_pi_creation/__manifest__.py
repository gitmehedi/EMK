{
    'name': 'Proforma Invoice (PI)',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'pi',
    'version':'1.0.0',
    'depends': [
        'stock',
        'gbs_application_group',
        'sales_team',
    ],

    'data': [
        'security/ir.model.access.csv',
        'wizards/tag_sale_order_view.xml',
        'views/proforma_invoice_view.xml',
    ],

    'summary': 'Proforma Invoice (PI) Creation',
    'installable': True,
    'application': False,
}