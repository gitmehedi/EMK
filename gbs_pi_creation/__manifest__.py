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
        'custom_report',
        'ir_sequence_operating_unit',
        'product_sales_pricelist',
        'samuda_so_type',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/proforma_invoice_view.xml',
        'report/proforma_invoice_report.xml',
        'data/pi_sequence.xml',
    ],

    'summary': 'Proforma Invoice (PI) Creation',
    'installable': True,
    'application': False,
}