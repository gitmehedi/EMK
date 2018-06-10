{
    'name': 'Sale By LC',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'10.0.1.0.0',
    'depends': [
        'sale',
        'letter_of_credit',
        'com_shipment',
        'shipment_lc_product',
        'gbs_pi_creation',
        'gbs_document_type',
        'custom_report',
        'amount_to_word_bd',
        'custom_report',
        'product_harmonized_system'
    ],

    'data': [
        'views/lc_sales_view.xml',
        'views/lc_sales_menu.xml',
        'views/shipment_sale_view.xml',
        'views/lc_sales_commercial.xml',
        'views/commercial_sales.xml',
        'reports/bank_top_sheet.xml',
        'reports/bill_of_exchange_first_report.xml',
        'reports/bill_of_exchange_second_report.xml',
        'reports/commercial_invoice_report_view.xml',
        'reports/beneficiary_certificate.xml',
        'reports/packing_list_report_view.xml',
        'reports/certificate_of_origin.xml',
        'reports/inspection_certificate.xml',
        'wizard/doc_receive_wizard_view.xml',
        'wizard/lc_sales_report_wizard.xml',
    ],

    'summary': 'Sale By LC',
    'installable': True,
    'application': False,
}