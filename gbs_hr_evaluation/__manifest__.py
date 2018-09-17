{
    'name': 'Employee Evaluation',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'This module maintain employees performance evaluation',
    'description': """
Periodical Employees evaluation and appraisals
==============================================

By using this application you can maintain the motivational process by doing periodical evaluations of your employees' performance. The regular assessment of human resources can benefit your people as well your organization.

An evaluation plan can be assigned to each employee. These plans define the frequency and the way you manage your periodic personal evaluations. You will be able to define steps and attach interview forms to each step.

Manages several types of evaluations: bottom-up, top-down, self-evaluations and the final evaluation by the manager.

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
        'date_range',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizard/hr_evaluation_employee_list_wizard_view.xml',
        'wizard/hr_performance_evaluation_wizard_view.xml',
        'views/hr_evaluation_plan_view.xml',
        'views/hr_evaluation_view.xml',
        'report/report_paperformat.xml',
        'report/hr_evaluation_report.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
