from odoo import models, fields, _
from odoo import api
from odoo.exceptions import ValidationError


class HrEarnedLeave(models.Model):
    _inherit = 'hr.holidays.status'

    leave_carry_forward = fields.Boolean(
        'Carry Forward this leave',
        help="If enabled, employee will be able to carry fwd leaves "
        "calculation.", default=True)


class LeaveForwardEncash(models.Model):
    _name = 'hr.leave.forward.encash'
    _description = 'HR Leave carry forward'
    _inherit = ['mail.thread']

    name = fields.Char(size=100, string='Title', required='True', readonly=False)

    leave_type = fields.Many2one('hr.holidays.status', string="Leave Type", required='True', ondelete='cascade', domain=[('leave_carry_forward','=',True)])

    """ Relational Fields """
    
    line_ids = fields.One2many('hr.leave.forward.encash.line','parent_id', string="Line Ids")

    exe_leave_year = fields.Many2one('date.range', string="Execution(Current) Year", required='True', domain="[('type_name', '=','Holiday Year' )]")

    company_id = fields.Many2one('res.company', string='Company', required='True',
                                 default=lambda self: self.env['res.company']._company_default_get())

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        required='True',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved")
    ], default='draft', track_visibility='onchange')

    @api.multi
    def action_approved(self):
        for values in self.line_ids:
            if values.carried_leave > 0:
                self.createLeaveByEmployee(values)

            line_obj = self.env['hr.leave.forward.encash.line'].search([('id', '=', values.id)])
            line_obj.write({'state': 'approved'})

        self.state = "approved"


    def createLeaveByEmployee(self, values):

        self.env['hr.holidays'].create({
            'name': ("Earn Leave From [%s]") % (self.carry_forward_year.name),
            'type': 'add',
            'number_of_days_temp': values.carried_leave,
            'holiday_type': 'employee',
            'holiday_status_id': self.leave_type.id,
            'employee_id': values.employee_id.id,
            'department_id': values.employee_id.department_id.id,
            'leave_year_id': self.exe_leave_year.id,
            'notes': ("Getting %s day(s) Earn Leave From [%s]") % (values.carried_leave,self.carry_forward_year.name),
            'state': 'validate',
        })

    @api.model
    def _default_leave(self):
        return self.env['date.range'].search([('type_name', '=','Holiday Year' )], limit=1)

    carry_forward_year = fields.Many2one('date.range', string="Encashment(Last) Year", required='True', domain="[('type_name', '=','Holiday Year' )]")

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    ####################################################
    # ORM Overrides methods
    ####################################################

    def unlink(self):
        for indent in self:
            if indent.state == 'approved':
                raise ValidationError(_('You cannot delete in this state'))

        return super(LeaveForwardEncash, self).unlink()