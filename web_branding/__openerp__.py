{
    'name': 'Web Branding',
    'category': 'Web',
    'summary': 'Change logo, website name',
    'author': 'Md. Mehedi Hasan',
    'website': 'https://github.com/gitmehedi',
    'depends': ['web','point_of_sale'],
    'data': [
        'views/web_template.xml',
        'views/pos_template.xml',
    ],
    'qweb': [
        'static/src/xml/pos_inherit.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
