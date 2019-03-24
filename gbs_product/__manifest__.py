{
    "name": "GBS PRODUCT",
    "author": "Genweb2 Ltd.",
    "website": "http://www.genweb2.com",
    "category": "Sale",
    "depends": [
        "gbs_application_group",
        "sale",
        "product",
        "purchase",
                ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/inherited_product_temp_gen_view.xml",
        "views/inherited_prod_temp_inven_view.xml",
    ],

    'installable': True,
    'application': False,
}