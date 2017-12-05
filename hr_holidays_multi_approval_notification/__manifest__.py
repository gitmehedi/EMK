{
    "name": "Holiday Multi Approvar Notification",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': "Genweb2 Limited <erp@genweb2.com>",
    "website": "http://genweb2.com",
    "category": "Human Resources",
    "summary": "Notify Employee Manager for Holiday Activity",
    "depends": [
        "hr_holidays_multi_levels_approval",
    ],
    "data": [
        'security/ir_rule.xml'
    ],
    'installable': True,
    'application': False,
}
