# -*- coding: utf-8 -*-

{
    'name': 'HR Exit Management Process',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Human Resource Management',
    'data': [
        'views/hr_exit_menu.xml',
        'views/checklist_type_view.xml',
        'views/checklist_item_view.xml',
        'views/configure_checklists_view.xml',
        'views/employee_exit_req_view.xml',
        'views/hr_checklist_employees_view.xml',
        'views/hr_configure_emp_checklists_view.xml',
        'workflow/emp_exit_req_workflow.xml',
        # 'wizard/employee_exit_search_popup.xml',
        # 'report/report_employee_exit.xml',
        # 'report/hr_exit_report.xml'
        # 'security/emp_exit_security.xml'
    ],
    'depends': ['hr'],
    'summary': 'HR exit process management',
    'category': 'HR Exit Management',
    'summary': 'HR exit process management ',
    'description': 'HR exit process management',
    'installable': True,
    'application': True,
}
