{
    'name': 'Letter of Credit (LC)',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'10.0.1.0.0',
    'depends': [
        # 'sale',
        'stock',
        'sales_team',
        'purchase',
        'commercial',
        'hr_employee_operating_unit',
        'base_bank_bd',
    ],

    'data': [
        'wizard/lc_wizard_view.xml',
        'views/letter_of_credit_view.xml',
        'views/letter_of_credit_menu.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],

    'summary': 'Letter of Credit (LC) Creation',
    'installable': True,
    'application': False,
}