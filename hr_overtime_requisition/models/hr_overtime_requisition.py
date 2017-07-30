from openerp import api
from openerp import models, fields,_
import datetime
from openerp.exceptions import UserError, ValidationError


class HROTRequisition(models.Model):
    _name='hr.ot.requisition'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    # # user access funtion
    # @api.one
    # @api.depends('employee_id')
    # def _compute_employee_check_user(self):
    #     user = self.env.user.browse(self.env.uid)
    #     if user.has_group('base.group_user'):
    #         if user.has_group('hr_attendance.group_hr_attendance_user') or user.has_group('gbs_base_package.group_dept_manager'):
    #             self.user_access=0
    #         else:
    #             self.user_access=1
    #     else:
    #         self.user_access = 0
    #
    # @api.one
    # @api.depends('employee_id')
    # def _compute_employee_check_hr_att_officer(self):
    #     user = self.env.user.browse(self.env.uid)
    #     if user.has_group('hr_attendance.group_hr_attendance_user'):
    #         self.user_access_hr_manager = 1
    #     else:
    #         self.user_access_hr_manager = 0
    #
    # @api.one
    # @api.depends('employee_id')
    # def _compute_employee_check_dept_manager(self):
    #     user = self.env.user.browse(self.env.uid)
    #     if user.has_group('gbs_base_package.group_dept_manager'):
    #         self.user_access_dept_manager = 1
    #     else:
    #         self.user_access_dept_manager = 0

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
    # user access fields
    # user_access_hr_att_officer= fields.Boolean(string='User Access Hr Manager', compute='_compute_employee_check_hr_att_officer',readonly=True)
    # user_access_dept_manager = fields.Boolean(string='User Access Department Manager',compute='_compute_employee_check_dept_manager',readonly=True)
    # user_access = fields.Boolean(string='User Access Normal', compute='_compute_employee_check_user',readonly=True)
    state = fields.Selection([
        ('to_submit', "To Submit"),
        ('to_approve', "To Approve"),
        ('hr_approve', "HR Approve"),
        ('approved', "Approved"),
        ('refuse', 'Refused'),
    ], default='to_submit')

    # @api.onchange('user_access_dept_manager')
    # def onchange_user_access_dept_manager(self):
    #     if self.user_access_hr_att_officer != True and self.user_access_dept_manager:
    #         return {'domain': {'employee_id': [('department_id.manager_id.user_id','=',self.env.user.id)]}}
    #     else:
    #         return {'domain': {'employee_id': [('operating_unit_id.id', '=', self.env.user.operating_unit_ids.ids)]}}

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
                if user.has_group('user_access_hr_att_officer'):
                    pass
                else:
                    raise UserError(_('You have no access to delete this record.'))
            return super(HROTRequisition, self).unlink()