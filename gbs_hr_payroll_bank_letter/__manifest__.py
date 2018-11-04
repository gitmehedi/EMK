{
    'name': 'GBS HR Payroll Bank Letter',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'payroll',
    'version': '10.0.1.0.0',
    'depends': [
        'gbs_hr_payroll',
        'amount_to_word_bd',
    ],
    'data': [
        'report/gbs_hr_payroll_report.xml',
        'report/payroll_report_bank_ac_view.xml',
        'wizard/hr_bank_letter_generate_wizard_views.xml',
        'views/hr_payslip_run_view.xml',
        'security/ir_rule.xml',
        'report/inherit_res_partner_bank_view.xml',
    ],

    'summary': 'Prints PDF report of Payslip for Bank Letter',
    'description':
        "Generate Bank Letter for Payslip",
    'installable': True,
    'application': True,
}
