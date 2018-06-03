{
    'name': 'Proforma Invoice (PI)',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'pi',
    'version':'10.0.1.0.0',
    'depends': [
        'stock',
        'gbs_application_group',
        'sales_team',
        'terms_setup',
        'custom_report'
    ],

    'data': [
        'security/ir.model.access.csv',
        #'wizards/tag_sale_order_view.xml',
        'views/proforma_invoice_view.xml',
        'report/proforma_invoice_report.xml',
    ],

    'summary': 'Proforma Invoice (PI) Creation',
    'installable': True,
    'application': False,
}