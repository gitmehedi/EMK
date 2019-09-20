# -*- coding: utf-8 -*-
{
    'name': "Purchase Quotation Compare",

    'summary': """
        Generate Report Base on Purchase Quotation""",

    'description': """
        This module generate the report to compare the quotation vale based on PR.
          In this report user can see comparision of different quotation. 
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Purchase',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_requisition','report_layout',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_view.xml',
        'report/template_purchaserequisitions.xml',
    ],
}