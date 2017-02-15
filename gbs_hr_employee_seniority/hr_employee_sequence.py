from openerp import models, fields
from openerp import api

class HrEmployeeSequenceInherit(models.Model):
    _inherit = ['hr.employee']
        
    employee_sequence = fields.Char(size=20, string='Emloyee Sequence')