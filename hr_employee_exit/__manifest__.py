# -*- coding: utf-8 -*-

{
    'name': 'HR Exit Management',
    'description': 'HR Exit Management',
    'summary': 'HR Exit Management',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'category': 'Human Resources',
    'depends': ['hr','gbs_application_group','mail'],
    'data': [
        'views/hr_exit_menu.xml',
        'views/checklist_type_view.xml',
        'views/checklist_item_view.xml',
        'views/configure_checklists_view.xml',
        'views/employee_exit_req_view.xml',
        'views/emp_exit_checklist_line.xml',
        'wizard/hr_checklist_generate_popup.xml',
        'views/mail_template.xml',
        'views/exit_interview.xml',
        'workflow/emp_exit_req_workflow.xml',
        # 'wizard/employee_exit_search_popup.xml',
        'report/report_employee_exit.xml',
        'report/report_emp_clearance.xml',
        'report/report_exit_interview.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml'
    ],
    'installable': True,
    'application': True,
}
