{
    'name' : 'GBS Account Invoice Report',
    'version' : '10.0.0.1',
    'summary': 'Custom Report of Account Invoice',
    'sequence': 300,
    'description': """
Invoicing & Payments
====================
The specific and easy-to-view report of account invoice.This is custom analytic report 
    """,
    'category': 'Accounting',
    'website': 'www.genweb2.com',
    'author': 'Genweb2 Limited',
    'depends' : ['account','sale', 'gbs_product', 'gbs_samuda_sales_access', 'gbs_procure_n_commercial_access'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_cron.xml',
        'report/account_invoice_report_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
