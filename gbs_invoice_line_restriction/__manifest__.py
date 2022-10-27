# -*- coding: utf-8 -*-
{
    'name': "GBS Invoice Line Qty Based On MRR or Delivery",

    'summary': """
    """,

    'description': """
    **This module restricts price unit and quantity field on Invoice Lines**
 
 
====================================================================================

* Vendor Bills(Rate and qty) from a purchase order cannot be edited.

* Vendor Bills qty will be loaded automatically from MRR qty and qty will be loaded from PO.

* Only Vendor Invoice Editor group can edit vendor bill line(Rate and qty)

* Customer Invoices manual create option omitted.

* Customer Invoices (Rate and qty) from a sale order cannot be edited.

* Service Order and Cnf Quotation Bills(Rate and qty) cannot be edited.

* In Refund or Out Refund Invoices can be edited. 
    """,

    'author': "Genweb2 Limited",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'stock_picking_mrr', 'gbs_application_group', 'gbs_samuda_service_order',
                'gbs_purchase_quotation_cnf', 'gbs_samuda_analytic_vendor_bills'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/inherited_vendor_bill.xml',
        'views/inherited_customer_invoice.xml',
    ],

}
