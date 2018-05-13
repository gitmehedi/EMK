# -*- coding: utf-8 -*-
{
    'name': "Stock Loan Analysis Report",

    'summary': """
        Analytical Report of Stock Loan Management.
        """,

    'description': """
        In this analytical Report user can see the all the record about stock loan and 
        get summary of it. Also can see the graphical view of the loan management.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': ['item_loan_process'],

    'data': [
        'security/ir.model.access.csv',
        'report/stock_loan_report_views.xml',
        'views/stock_loan_analysis_view.xml',
    ],

}