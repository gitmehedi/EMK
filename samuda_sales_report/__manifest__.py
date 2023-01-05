# -*- coding: utf-8 -*-
{
    'name': 'Samuda Sales Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Samuda Sales Reports',
    'version': '10.0.0.1',
    'depends': [
        'account',
        'sales_team',
        'samuda_sales_country'
    ],
    'data': [
        'reports/executive_sales_report.xml',
        'reports/customer_sales_report.xml',
        'reports/customer_sales_sector_report.xml',
        'reports/sector_sales_product_report.xml',
        'reports/outstanding_statement_report.xml',
        'reports/credit_details_product_report.xml',
        'reports/yearly_sales_comparison_report.xml',
        'reports/daily_delivery_statement_report.xml',
        'reports/daily_undelivered_statement_report.xml',
        'reports/monthly_delivery_executive_report.xml',
        'reports/monthly_delivery_product_report.xml',
        'wizard/customer_aging_statement_wizard.xml',
        'wizard/executive_sales_wizard.xml',
        'wizard/customer_sales_wizard.xml',
        'wizard/customer_sales_sector_wizard.xml',
        'wizard/sector_sales_product_wizard.xml',
        'wizard/outstanding_statement_wizard.xml',
        'wizard/credit_details_product_wizard.xml',
        'wizard/yearly_sales_comparison_wizard.xml',
        'wizard/daily_delivery_statement_wizard.xml',
        'wizard/daily_undelivered_statement_wizard.xml',
        'wizard/monthly_delivery_executive_wizard.xml',
        'wizard/monthly_delivery_product_wizard.xml',
        'reports/customer_aging_statement.xml',
        'reports/inherited_views.xml',
        'view/menu_items.xml',
        'wizard/sale_under_over_approved_price_wizard.xml',
        'reports/sale_under_over_approved_price_view.xml',
    ],

    'summary': 'Samuda Sales Reports Information',
    'installable': True,
    'application': True,
}