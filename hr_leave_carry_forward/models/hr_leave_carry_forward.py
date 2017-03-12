from openerp import models, fields
from openerp import api

class HrLeaveLeave(models.Model):    
    _name = 'hr.leave.carry.forward'
    _description = 'HR Leave carry forward'    

    name = fields.Char(size=100, string='Title', required='True')
    carry_forward_year = fields.Char(size=10, string='Leave Year', required='True')
    leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True')
    
    
    """ Relational Fields """
    
    line_ids = fields.One2many('hr.leave.carry.forward.line','parent_id', string="Line Ids")
    
    
    """@api.onchange('partner_id')
    def _onchange_partner_id(self):
        res, ids = {}, []
        self.style_id = 0
        self.department_id = 0

        if self.partner_id:
            for obj in self.partner_id.styles_ids:
                if obj.version==1 and obj.state == 'confirm':
                   ids.append(obj.id)

        res['domain'] = {
                    'style_id':[('id', 'in', ids)],
                }
        
        return res
"""    
    
    
  