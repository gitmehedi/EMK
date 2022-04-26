{
    'name': 'Excel Report For Petty Cash',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Gbs Samuda Petty Cash',
    'version': '10.0.1.0.0',
    'depends': [
        'account','base', 'report_xlsx', 'report'
               ],

    'data': [
        'views/inherited_acc_bank_statement_button_add_view.xml',
        'report/petty_cash_report_xlsx_view.xml'

    ],

    'summary': 'Excel Report For Petty Cash',
    'description':
        """This module print report for Petty Cash
            based on the condition'""",
    'installable': True,
    'application': True,
}
