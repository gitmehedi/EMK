{
    "name": "GBS Collection LC",
    "version": "10.0.0.1",
    "category": "Accounting",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    "summary": "LC Collection Payments",
    "description":"Customize module for LC Collections.",
    "depends": [
        "account",
        "com_shipment",
        "lc_sales_product",
        "account_cost_center"
    ],
    'data': [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/data.xml",
        "data/lc_journal_data.xml",
        "views/lc_receivable_payments_view.xml",
    ],
    'installable': True,
    'application': False,
}
