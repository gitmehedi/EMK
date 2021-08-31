{
    'name': 'Membership Users',
    'description': """ All users of membership""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'membership',
        'partner_fullname',
        'membership_card',
        'membership_extension',
        'membership_variable_period',
        'membership_remaining_days',
    ],
    'data': [
        'security/users.xml',
    ],
    'installable': True,
}