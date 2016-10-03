# -*- coding: utf-8 -*-

{
    'name': 'POS Date & Time Formats',
    'version': '1.2',
    'category': 'Point Of Sale',
    'sequence': 3,
    'author': 'Mostafa Mohamed',
    'summary':
        'Change/Modify Receipt Datetime Format in your Odoo Point-Of-Sale Configuration.',
    'description': """
    Change/Modify Receipt Datetime Format in your Odoo Point-Of-Sale Configuration.
    """,
    'depends': ["point_of_sale"],
    'data': [
        'date_time_change/date_time_change_view.xml',
        'more_formats/more_formats_view.xml',
        'views/template.xml',
    ],
    'qweb': [
        'static/src/xml/pos_enhanced.xml',
    ],
    "images": ["static/description/1.jpg",
               "static/description/1.png",
               "static/description/2.png",
               "static/description/3.png",
               "static/description/4.png",
               "static/description/5.png", ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
