{
    "name": "GBS LC Collection Payments",
    "version": "10.0.0.1",
    "category": "Accounting",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    "summary": "LC Collection Payments",
    "description":"Customize module for LC Collections.",
    "depends": ["account","com_shipment","lc_sales_product"],
    'data': [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/lc_receivable_payments_view.xml",
    ],
    'installable': True,
    'application': False,
}