from odoo import models, fields,api

class HrEmployeeLoanProof(models.Model):
    _name = 'hr.employee.loan.proof' 
    _description = 'hr employee loan proof'   

    name = fields.Char(size=100, string='Name', required='True')
    mandatory = fields.Boolean(string='Mandatory', default=True)

    """All function which process data and operation"""
    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')