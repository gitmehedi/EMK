# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Half Day Leave Management',
    'summary': 'Holidays, Allocation and Leave Requests in Hours',
    'author': 'Genweb2',
    'website': 'http://www.genweb2.com',
    'sequence': 55,
    'category': 'Human Resources',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
        'date_range',

    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_holidays.xml',
    ],
    'installable': True,
}
