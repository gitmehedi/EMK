{
    'name': 'HR Employee OT Other Deduction',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR OT Other Deduction',
    'version': '10.0.1.0.0',
    'depends': [
                'hr_payroll',
                'hr',
                'hr_other_deduction'
               ],

    'data': [
        'views/hr_other_deduction_ot.xml'
    ],

    'summary': 'Calculates HR Other Deduction OT Information',
    'description':
        """This module calculates the  other deduction ot of the employee
            based on the condition'""",
    'installable': True,
    'application': True,
}