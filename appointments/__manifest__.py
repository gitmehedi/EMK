# -*- coding: utf-8 -*-
{
    'name': 'Appointment and Booking Management',
    'description': """ All types of users whom are related to activities of Appointment and Booking Management""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Appointment',
    'depends': [
        'base',
        'mail',
        'gbs_gender',
        'appointment_user',
        'appointment_menu',
    ],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'reports/reports.xml',
        'data/mail_template.xml',
        'reports/visiting_info.xml',
        'wizards/appointment_wizard_views.xml',
        'views/appointment_templates.xml',
        'views/appointment_type_views.xml',
        'views/appointment_topics_views.xml',
        'views/meeting_room_views.xml',
        'views/appointment_contact_views.xml',
        'views/appointment_timeslot_views.xml',
        'views/appointment_views.xml',
    ],
    'installable': True,
}

