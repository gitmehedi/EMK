from openerp import models, fields

class HrEmployeeLoanInstallmentPayment(models.Model):
    _name = 'hr.employee.loan.installment.payment'    

    name = fields.Char(size=100, string='Name', required='True')
    code = fields.Char(size=100, string='Code', required='True')
    date = fields.Date(string="Date")
             