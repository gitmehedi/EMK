# -*- coding: utf-8 -*-
{
    'name': "Local LC Sales Report",

    'summary': """
        Custom Report For local LC Sales""",

    'description': """
        From Here user can able to print record of local lc sales .
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",

    'category': 'Commercial',
    'version': '10.0.1',

    'depends': ['lc_sales_product_local'],

    'data': [
        # 'security/ir.model.access.csv',
        'wizard/lc_sales_local_wizard_view.xml',
        'report/local_first_acceptance_report.xml',
        'report/local_second_acceptance_report.xml',
        'report/lc_sales_local_maturity_report.xml',
    ]
}