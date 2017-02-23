from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    
    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            department_name = self.search(filters)
            if len(department_name) > 1:
                raise Warning('[Unique Error] name already exists and violates unique field constraint')