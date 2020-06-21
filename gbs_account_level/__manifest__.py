{
    "name": "Account Level",
    "summary": "Define the level of Chart of Accounts",
    "category": "Accounting",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/level_data.xml",
        "views/account_level_views.xml",
    ],
    "application": False,
    "installable": True,
}
