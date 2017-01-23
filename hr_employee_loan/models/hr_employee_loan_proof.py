from openerp import models, fields

class HrEmployeeLoanProof(models.Model):
    _name = 'hr.employee.loan.proof' 
    _description = 'hr employee loan proof'   

    name = fields.Char(size=100, string='Name', required='True')
    mand = fields.Boolean(string='Mandatory', default=False)
    
             