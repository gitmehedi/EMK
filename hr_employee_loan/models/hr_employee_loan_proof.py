from openerp import models, fields

class HrEmployeeLoanProof(models.Model):
    _name = 'hr.employee.loan.proof'    

    name = fields.Char(size=100, string='Title', required='True')
             