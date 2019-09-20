{
    "name": "HR Employee Operating Unit",
    "author": "Genweb2 Ltd.",
    "website": "http://www.genweb2.com",
    'sequence': 101,
    "category": "Human Resources",
    "depends": ["hr", "operating_unit",
                # "gbs_application_group",
                ],
    "data": [
        "views/hr_views.xml",
        "security/hr_emp_security.xml",
    ],

    'installable': True,
    'application': True,
}
