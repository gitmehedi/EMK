{
    'name': 'GBS Samuda Procure To Pay Installation',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Sales',
    'depends': [
        'base_suspend_security',
        'stock_indent',
        'ir_sequence_operating_unit',
        'indent_type',
        'indent_operating_unit',
        'stock_operating_unit_user',
        'gbs_purchase_requisition',
        'gbs_purchase_order',
        'shipment_lc_product',
        'letter_of_credit',
        'lc_po_product',
        'com_shipment',
        'commercial',
        'gbs_purchase_quotation_cnf',
        'product_gate_in',
        'purchase_quotation_compare',
        'letter_of_credit_done',
        'gbs_stock_product',
        'web_access_rule_button_extend',
        'letter_of_credit_report',
        'stock_gate_in',
        'stock_incoterms_extend',
        'gbs_supplier',
        'gbs_purchase_rfq',
        'gbs_po_merge',
        'terms_setup_foreign',
        'terms_setup_local',
        'gbs_purchase_mrr',
        'purchase_reports'
    ],

    'data': [ ],
    'description': 'Install all modules which is related with procure to pay',
    'installable': True,
    'application' : True,
}