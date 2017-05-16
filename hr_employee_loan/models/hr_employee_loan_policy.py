from openerp import models, fields,api

class HrEmployeeLoanPolicy(models.Model):
    _name = 'hr.employee.loan.policy'    

    name = fields.Char(size=100, string='Name', required='True')
    code = fields.Char(size=100, string='Code', required='True')
    value = fields.Float(size=100, string='Value', required='True')
    
    """ All relations fields """
    employee_ids = fields.Many2many('hr.employee', string='''Employee's''')
    employee_tag_ids = fields.Many2many('hr.employee.category', string='Employee Catagories')
    
    policy_type_id = fields.Selection([
        ('flat', 'Max Loan Amount'),
        ('incremental', 'Gap Between Two Loans'),
        ('period', 'Qualifying Period'),
        ], string = 'Policy Type',required='True')
    
    company_id = fields.Many2one('res.company', string='Company',ondelete='cascade', default=lambda self: self.env.user.company_id)
    basis_id = fields.Selection([
        ('flat', 'Fix Amount')], string = 'Basis',required='True')

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')