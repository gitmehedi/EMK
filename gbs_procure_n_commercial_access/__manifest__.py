# -*- coding: utf-8 -*-
{
    'name': "GBS Procure To Pay & Commercial Access",

    'summary': """
        This module will install base required addons.""",

    'description': """
        This module will install base required addons for Samuda chemical.  
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'category': 'Tools',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'commercial',
                'purchase',
                'letter_of_credit',
                'gbs_purchase_requisition',
                'gbs_purchase_order',
                'gbs_purchase_quotation_cnf',
                'stock_operating_unit_user',
                'purchase_requisition',
                'question_set',
                'letter_of_credit_done',
                'lc_po_product',
                'indent_operating_unit',
                'question_set',
                'com_shipment',
                'gbs_application_group',
                'shipment_lc_product',
                'product_gate_in',
                'letter_of_credit_report',
                'gbs_document_type',
                'terms_setup',
                'stock_operating_unit',
                'stock',
                'terms_setup_foreign',
                'terms_setup_local',
                'gbs_supplier',
                'gbs_purchase_rfq',
                'gbs_po_merge',
                'purchase_reports',
                'gbs_purchase_mrr',
                'gbs_service',
    ],


    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/menu_items.xml',
        'views/field_items.xml',
        'views/commercial_po_menu.xml',
        'views/commercial_supplier_menus.xml',
    ],
}