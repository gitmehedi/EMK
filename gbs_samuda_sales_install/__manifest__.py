
{
    'name': 'GBS Samuda Sales Installation',
    'version': '1.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Sales',
    'depends': [
        'gbs_sales_commission',
        'customer_credit_limit',
        'gbs_sales_commission',
        'gbs_sales_commission_so',
        'gbs_sale_delivery_settings',
        'gbs_product',
        'product_sales_pricelist',
        'delivery_order',
        'gbs_sale_order_approval',
        'sale_order_type',
        'sale_order_revision',
        #'sale_revision_history'
    ],

    'data': [ ],
    'description': 'Install all modules which is related with sales',
    'installable': True,
    'application' : True,
}