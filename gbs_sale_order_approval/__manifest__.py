{
    'name': 'Order to Cash Process',
    'version': '10.1.0.1',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles Sale Order requisition in a customized business logic way.",
    'depends': [
        'gbs_application_group',
        'sale',
        'product',
        'sales_team',
        'gbs_sales_commission',
        'gbs_sales_commission_so',
        'delivery_order',
        'samuda_so_type',
        'operating_unit',
        'amount_to_word_bd',
        'letter_of_credit',
        'gbs_pi_creation',
        'account',
        'ir_sequence_operating_unit',
        'report_layout',
        'sale_stock', ## to hide delivery menu. it is inherited on this module
        'terms_setup',
        'account_cost_center'
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/inherited_sale_view.xml',
        'views/sales_channel_view.xml',
        'views/menuitems.xml',
        'views/res_partner_views.xml',
        'report/inherit_sale_order_report.xml',
        'data/sale_order_sequence.xml',

    ],
    'installable': True,
    'application': False,
}
