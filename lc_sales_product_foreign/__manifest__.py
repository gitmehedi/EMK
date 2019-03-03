{
    'name': 'Foreign LC Sales Function',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'10.0.1.0.0',
    'depends': [
        'lc_sales_product',
    ],

    'data': [
        'views/lc_sales_view.xml',
        'views/shipment_sale_view.xml',
        'views/lc_sales_commercial.xml',
        'reports/packing_list_report_view.xml',
        'reports/commercial_invoice_report_view.xml',
        'reports/bill_of_exchange_report.xml',
        'reports/certificate_of_origin.xml',
        'wizard/lc_sales_report_wizard.xml',
        'wizard/doc_receive_wizard_view.xml',
        'wizard/sales_invoice_export_wizard_view.xml',
        'wizard/lc_sales_report_wizard.xml',
        'wizard/seller_bank_export_wizard_view.xml',
        'wizard/buyer_bank_export_wizard_view.xml',
        'wizard/lc_amendment_wizard_view_foreign.xml',
        'wizard/maturity_export_wizard_view_foreign.xml',
        'views/lc_sales_menu.xml',
    ],

    'summary': 'Sale By LC',
    'installable': True,
    'application': False,
}