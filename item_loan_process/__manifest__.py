# -*- coding: utf-8 -*-
{
    'name': "Item Loan Process",

    'summary': """This process manage the item loan management""",

    'description': """
        This process usually manage, when the company/factory has inadequate items/goods, in that
case company/factory can take loan from others. After taking that loan, it will have loan re-
payment option for that specific loan. The re-payment can be done by goods or amount wise
based on the contract between two parties. There might be another case where another company
may take loan from company/factory. In that scenario, company/factory will receive goods/amount for giving
the loan to other company. System will handle the both case mentioned above.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Inventory',
    'version': '10.0.0.1',

    'depends': ['base','mail','product'],

    'data': [
        'security/ir.model.access.csv',
        'views/item_loan_borrowing_process_views.xml',
        'views/item_loan_lending_process_views.xml',
    ],

}