# -*- coding: utf-8 -*-
# © 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "GBS HR Attendance Grace Time",
    "summary": """""",
    "version": "1.0.0",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ['hr',
        'hr_attendance'],
    "data": [
        "views/hr_attendance_grace_time_views.xml",
    ],
    'installable': True,
    'application': True
}
