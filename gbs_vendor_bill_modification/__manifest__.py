# -*- coding: utf-8 -*-
{
    'name': "GBS Vendor Bill Modification",

    'summary': """
    """,

    'description': """
    
* Vendor Bills(Rate and qty) from a purchase order cannot be edited.

* MRR Option in Vendor Bills

* MRR wise bill generation

* Vendor Bills qty will be loaded automatically from MRR qty and qty will be loaded from PO.

* Only Vendor Invoice Editor group can edit vendor bill line(Rate and qty)

* Service Order and Cnf Quotation Bills(Rate and qty) cannot be edited.

* In Refund or Out Refund Invoices can be edited. 
    """,

    'author': "Genweb2 Limited",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'stock_picking_mrr','account_cancel', 'gbs_application_group', 'gbs_samuda_service_order',
                'gbs_purchase_quotation_cnf', 'gbs_samuda_analytic_vendor_bills'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/inherited_purchase_config_settings_views.xml',
        'views/inherited_vendor_bill.xml',
        'views/invoice_cancellation_wizard.xml'
    ],

}
