{
    'name': 'HR Attendance and Over Time (OT) Summary',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_summary_view.xml',
        'wizards/attendance_summary_wizard_views.xml',
        'report/hr_attendance_and_ot_summary_report.xml',
        'report/hr_attendance_and_ot_summary_report_templates.xml',
    ],
    
    'depends': [
        'hr_attendance',
        'hr',
        'hr_holidays',
        'gbs_hr_calendar',
    ],    
    
    'description': 
    """This module will show attendance and over time summary at a glance of employees""",        
    'installable': True,
    'application': True,
}