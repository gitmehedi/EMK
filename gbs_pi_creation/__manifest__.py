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
        'account',
        'terms_setup',
        'report_layout',
        'ir_sequence_operating_unit',
        'product_sales_pricelist',
        'samuda_so_type',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/proforma_invoice_view.xml',
        'report/proforma_invoice_report.xml',
        'data/pi_sequence.xml',
    ],

    'summary': 'Proforma Invoice (PI) Creation',
    'installable': True,
    'application': False,
}