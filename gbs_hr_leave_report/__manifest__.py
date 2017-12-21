{
    'name': 'HR Leave Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',    
    'version':'1.0',
    'data': [       
       'wizard/hr_holidays_summary_department_views.xml',
       'report/gbs_hr_leave_report.xml',
       'report/gbs_hr_leave_report_templates.xml',
       'report/leave_summary_report.xml',
    ],
    'depends': [
       'hr_holidays',
       'hr',
       'gbs_hr_calendar',
       'gbs_operating_unit',
       'hr_employee_operating_unit',
       'base',
       'report',
    ],    
    
    'description': """This module enables HR Manager to generate leave related reports in PDF format""",        
  
    'installable': True,
    'application': True,
}