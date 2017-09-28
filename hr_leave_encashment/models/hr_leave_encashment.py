from odoo import models, fields
from odoo import api

class HrEarnedLeave(models.Model):    
    _inherit = 'hr.holidays.status'
    
    earned_leave_encashment = fields.Boolean(
        'Encash this leave ',
        help="If enabled, employee will be able to encash their leave", default=True) 

class HrLeaveLeave(models.Model):    
    _name = 'hr.leave.encashment'
    _description = 'HR Leave Encashment'


    @api.model
    def _default_leave(self):
        return self.env['hr.leave.fiscal.year'].search([], limit=1)

    name = fields.Char(size=100, string='Title', required='True')
    encashment_year = fields.Many2one('hr.leave.fiscal.year', string="Leave Year", default=_default_leave, required='True')

    """ Relational Fields """
    leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True',
                                 ondelete='cascade', domain=[('earned_leave_encashment', '=', True)])
    line_ids = fields.One2many('hr.leave.encashment.line','parent_id', string="Line Ids")
    
    
    # _sql_constraints=[
    #     ('leave_type_unique','unique(leave_type)','[Unique Errror] Leave Type must be unique!'),
    # ]


    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name)>1:
                raise Warning('[Unique Error] Name must be unique!')