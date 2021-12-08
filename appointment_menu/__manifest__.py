{
    'name': 'Appointment Management Menu',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Appointment',
    "sequence": 10,
    'summary': 'Install all modules inside Appointment functionality',
    'description': """
    Install all modules inside Appointment functionality.
    """,
    'depends': [
        'appointment_user',
    ],
    'data': [
        'views/menu.xml'
    ],
    'installable': True,
    'application': True,
}
