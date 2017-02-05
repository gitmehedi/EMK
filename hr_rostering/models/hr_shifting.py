from openerp import api
from openerp import fields
from openerp import models

class HrShifting(models.Model):
   # _name = 'hr.shifting'
    _inherit = ['resource.calendar.attendance']
    

    #Fields of Model    
    ot_hour_from = fields.Float(string='OT from')
    ot_hour_to = fields.Float(string='OT to')
    isIncludedOt =  fields.Boolean(string='Is it included OT', default=False)    
    calendar_id = fields.Many2one("resource.calendar", string="Resource's Calendar", required=False)
    