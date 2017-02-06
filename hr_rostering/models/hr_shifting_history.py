from openerp import fields
from openerp import models


class HrShifting(models.Model):
   _name = 'hr.shifting.history'
   _order = "effective_from DESC"
   
   #Fields of Model
   effective_from = fields.Date(string='Effective Date')
   employee_id =  fields.Many2one("hr.employee", string='Employee Name', required=True)    
   shift_id = fields.Many2one("resource.calendar", string="Shift Name", required=True)