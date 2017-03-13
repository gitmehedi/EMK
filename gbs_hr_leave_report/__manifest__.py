{
    'name': 'HR Leave Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',    
    'version':'1.0',
    'data': [       
       'report/gbs_hr_leave_report.xml',  
       'report/gbs_hr_leave_report_templates.xml',          
    ],    
    'depends': [
       'hr_holidays', 
    ],    
    
    'description': """This module enables HR Manager to generate leave related reports in PDF format""",        
  
    'installable': True,
    'application': True,
}