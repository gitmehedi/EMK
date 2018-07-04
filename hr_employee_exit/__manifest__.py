# -*- coding: utf-8 -*-

{
    'name': 'HR Exit Management',
    'description': 'HR Exit Management',
    'summary': 'HR Exit Management',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'category': 'Human Resources',
    'depends': ['hr','gbs_application_group'],
    'data': [
        'views/hr_exit_menu.xml',
        'views/checklist_type_view.xml',
        'views/checklist_item_view.xml',
        'views/configure_checklists_view.xml',
        'views/employee_exit_req_view.xml',
        'wizard/hr_checklist_generate_popup.xml',
        'views/hr_emp_master_checklists_view.xml',
        'workflow/emp_exit_req_workflow.xml',
        # 'wizard/employee_exit_search_popup.xml',
        'report/report_employee_exit.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml'
    ],
    'installable': True,
    'application': True,
}
