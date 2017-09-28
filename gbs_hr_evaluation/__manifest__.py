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
        'gbs_base_package',
        'gbs_application_group',
        'gbs_hr_attendance',
        'gbs_hr_holidays',
        'hr_employee_operating_unit',
        'hr_holiday_notification',
    ],
    'data': [
        'wizard/hr_evaluation_employee_list_wizard_view.xml',
        'views/hr_evaluation_plan_view.xml',
        'views/hr_evaluation_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
