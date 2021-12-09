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
        'appointment_user',
        'appointment_menu',
    ],
    'data': [
        'views/appointment_type_views.xml',
        'views/appointment_topics_views.xml',
        'views/meeting_room_views.xml',
        'views/appointment_contact_views.xml',

    ],
    'installable': True,
}

