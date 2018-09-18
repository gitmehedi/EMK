{
    'name': 'GBS HR Payroll Top Sheet',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'payroll',
    'version': '10.0.1.0.0',
    'depends': [
        'report_layout',
        'amount_to_word_bd',
        'gbs_hr_payroll',
    ],
    'data': [
        'report/payroll_top_sheet_report_view.xml',

    ],
    'summary': '',
    'description':" This module shows monthly emplyee's salary top sheet report",
    'installable': True,
    'application': True,
}
