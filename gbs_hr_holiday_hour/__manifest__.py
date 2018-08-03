# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Leave Management in hours',
    'summary': 'Holidays, Allocation and Leave Requests in Hours',
    'author': 'Genweb2',
    'website': 'http://www.genweb2.com',
    'category': 'Human Resources',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'sequence': 35,
    'depends': [
        'hr_short_leave',
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays.xml',
    ],
    'installable': True,
}
