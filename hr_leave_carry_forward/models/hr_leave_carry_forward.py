from odoo import models, fields
from odoo import api


class HrEarnedLeave(models.Model):
    _inherit = 'hr.holidays.status'

    leave_carry_forward = fields.Boolean(
        'Carry Forward this leave',
        help="If enabled, employee will be able to carry fwd leaves "
        "calculation.", default=True)


class HrLeaveLeave(models.Model):    
    _name = 'hr.leave.carry.forward'
    _description = 'HR Leave carry forward'

    name = fields.Char(size=100, string='Title', required='True')
    #carry_forward_year = fields.Many2one('hr.leave.fiscal.year', string="Leave Type", required='True')
    leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True',ondelete='cascade',domain=[('leave_carry_forward','=',True)])

    """ Relational Fields """
    
    line_ids = fields.One2many('hr.leave.carry.forward.line','parent_id', string="Line Ids")

    @api.model
    def _default_leave(self):
        return self.env['hr.leave.fiscal.year'].search([], limit=1)

    carry_forward_year = fields.Many2one('hr.leave.fiscal.year', string="Leave Year", default=_default_leave, required='True')

    # _sql_constraints = [
    #     ('leave_type_unique', 'unique(leave_type)','[Unique Error] Leave Type must be unique!'),
    # ]

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')