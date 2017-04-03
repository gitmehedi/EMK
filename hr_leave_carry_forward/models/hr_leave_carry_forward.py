from openerp import models, fields
from openerp import api


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
    # leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True',
    #                              ondelete='cascade')
    leave_type = fields.Many2one("hr.holidays.status", string="Leave Type", required=True)
    """ Relational Fields """
    
    line_ids = fields.One2many('hr.leave.carry.forward.line','parent_id', string="Line Ids")

    @api.model
    def _default_leave(self):
        return self.env['hr.leave.fiscal.year'].search([], limit=1)

    carry_forward_year = fields.Many2one('hr.leave.fiscal.year', string="Leave Year", default=_default_leave, required='True')