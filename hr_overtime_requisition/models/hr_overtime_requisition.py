from openerp import api
from openerp import models, fields,_
import datetime
from openerp.exceptions import UserError, ValidationError


class HROTRequisition(models.Model):
    _name='hr.ot.requisition'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
                                  default=_default_employee,required=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    readonly=True, store=True)
    from_datetime = fields.Datetime('Start Date', readonly=True, index=True, copy=False,required=True)
    to_datetime = fields.Datetime('End Date', readonly=True, copy=False,required=True)
    total_hours = fields.Float(string='Total hours', compute='_compute_total_hours', store=True,digits=(15, 2),readonly=True)
    ot_reason = fields.Text(string='Reason for OT')

    first_approval = fields.Boolean('First Approval', compute='compute_check_first_approval')

    state = fields.Selection([
        ('to_submit', "To Submit"),
        ('to_approve', "To Approve"),
        ('hr_approve', "HR Approve"),
        ('approved', "Approved"),
        ('refuse', 'Refused'),
    ], default='to_submit')


    @api.constrains('to_datetime')
    def _check_to_datetime_validation(self):
        if self.to_datetime < self.from_datetime:
            raise ValidationError(_("End Time can not less then Start Time!!"))


    @api.depends('from_datetime', 'to_datetime')
    def _compute_total_hours(self):
        if self.from_datetime and self.to_datetime:
            start_dt = fields.Datetime.from_string(self.from_datetime)
            finish_dt = fields.Datetime.from_string(self.to_datetime)
            diff=finish_dt-start_dt
            hours = float(diff.total_seconds()  / 3600)
            self.total_hours = hours

    # _sql_constraints = [
    #     ('duration_check', "CHECK ( total_hours >= 0 )", "Duration must be greater than 0."),
    # ]

    @api.multi
    def action_submit(self):
        self.write({'state': 'to_approve'})

    @api.multi
    def action_hod_approve(self):
        self.write({'state': 'hr_approve'})

    @api.multi
    def action_hr_approve(self):
        self.write({'state': 'approved'})

    @api.multi
    def action_refuse(self):
        self.write({'state': 'refuse'})

    @api.multi
    def action_reset(self):
        self.write({'state': 'to_submit'})

    @api.multi
    def unlink(self):
        for a in self:
            if a.state != 'to_submit':
                user = a.env.user.browse(self.env.uid)
                if user.has_group('hr_attendance.group_hr_attendance_user'):
                    pass
                else:
                    raise UserError(_('You have no access to delete this record.'))
            return super(HROTRequisition, self).unlink()

    ### User and state wise approve button hide function
    @api.multi
    def compute_check_first_approval(self):
        for h in self:
            if h.state != 'to_approve':
                h.first_approval = False
            ### no one can approve own request
            elif h.employee_id.user_id.id == self.env.user.id:
                h.first_approval = False
            else:
                res = h.employee_id.check_1st_level_approval()
                h.first_approval = res