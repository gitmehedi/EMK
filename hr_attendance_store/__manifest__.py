# -*- coding: utf-8 -*-

{
    "name": "HR Attendance Collection",
    "summary": "HR Attendance Collection",
    "version": "10.0.0.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'license': "AGPL-3",
    "category": "Tools",
    "depends": [
        'mail',
        'account',
        'hr',
        'hr_attendance',
        'hr_manual_attendance',
    ],
    "data": [
        # "data/ir_cron.xml",
        # "views/menu_view.xml",
        "wizards/hr_manual_attendance_process_wizard_view.xml",
        "views/hr_attendance_terminal_view.xml",
        "views/hr_attendance_card_view.xml",
        "views/hr_manual_attendance_process_view.xml",
    ],
    "application": True,
    "installable": True,
}
