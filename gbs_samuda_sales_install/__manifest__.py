
{
    'name': 'GBS Samuda Sales Installation',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Sales',
    'depends': [
        'gbs_sales_commission',
        'customer_credit_limit',
        'gbs_sales_commission_so',
        'gbs_sale_delivery_settings',
        'gbs_product',
        'product_sales_pricelist',
        'delivery_order',
        'gbs_sale_order_approval',
        'sale_order_type',
        'sale_order_revision',
        'samuda_so_type',
        'letter_of_credit',
        'gbs_pi_creation',
        'delivery_schedules',
        'gbs_application_group'
        'delivery_invoicing',
        #'sale_revision_history'
    ],

    'data': [ ],
    'description': 'Install all modules which is related with sales',
    'installable': True,
    'application' : True,
}