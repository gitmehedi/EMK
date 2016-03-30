from openerp import models, fields, api

class HrHolidaysExtended(models.Model):
       _inherit = 'hr.holidays'
       
       officer_id = fields.Many2one('res.users', string='HR Officer', compute = '_get_officer_id', store=True)
       
       @api.depends('employee_id')
       def _get_officer_id(self):
           print "..........................................................................................................................."
           if(self.employee_id.parent_id):
               print "test......................................................................................................."
               self.officer_id = self.employee_id.parent_id.user_id.id
           
     