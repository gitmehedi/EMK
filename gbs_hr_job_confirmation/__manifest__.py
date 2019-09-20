{
    'name': 'Employee Job Confirmation',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'This module maintain employees Job Confirmation',
    'description': """
Periodical Employees Job Confirmation
==============================================

By using this application you can maintain the motivational process by doing periodical job confirmations of your employees' performance. The regular assessment of human resources can benefit your people as well your organization.

An job confirmation plan can be assigned to each employee. These plans define the frequency and the way you manage your periodic personal job confirmations. You will be able to define steps and attach interview forms to each step.

Manages several types of job confirmations: bottom-up, top-down and the final job confirmation by the manager.

    """,
    'author': "Genweb2",
    'website': "http://www.genweb2.com",
    'depends': [
        'hr',
        'hr_holidays',
        'hr_attendance',
        'gbs_application_group',
        'operating_unit',
        'question_set',
        'hr_employee_seniority',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizard/hr_job_confirmation_employee_list_wizard_view.xml',
        'wizard/hr_job_confirmation_wizard_view.xml',
        'views/hr_job_confirmation_plan_view.xml',
        'views/hr_job_confirmation_view.xml',
        #'report/report_paperformat.xml',
        #'report/hr_evaluation_report.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
