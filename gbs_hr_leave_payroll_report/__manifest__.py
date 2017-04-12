{
    'name': 'HR Leave Payroll Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',    
    'version':'1.0',
    'data': [       
       'report/gbs_hr_leave_report.xml',  
       'report/gbs_hr_leave_report_templates.xml',
       'report/gbs_hr_payroll_report.xml',
       'report/payroll_report_view.xml',
    ],    
    'depends': [
       'hr_holidays',
       'hr_payroll', 
       'gbs_hr_employee_seniority',
    ],    
    
    'description': """This module enables HR Manager to generate leave and payroll related reports in PDF format""",        
  
    'installable': True,
    'application': True,
}