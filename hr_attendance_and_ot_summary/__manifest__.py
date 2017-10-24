{
    'name': 'HR Attendance and Over Time (OT) Summary',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
        'report/report_paperformat.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/attendance_summary_view.xml',
        'wizards/attendance_summary_wizard_views.xml',
        'report/hr_attendance_summary_report_template.xml',
        'report/hr_attendance_summary_report_view.xml',

    ],
    
    'depends': [
        'hr_attendance',
        'hr',
        'hr_holidays',
        'gbs_hr_calendar',
        'gbs_hr_employee_sequence',
        'gbs_hr_department_sequence',
        'gbs_hr_attendance_error_correction',
        'hr_employee_operating_unit',
        'hr_overtime_requisition',
    ],    
    
    'description': 
    """This module will show attendance and over time summary at a glance of employees""",        
    'installable': True,
    'application': True,
}