from openerp import api
from openerp import models, fields,_,SUPERUSER_ID
import datetime
from openerp.exceptions import UserError, ValidationError

class HrManualAttendance(models.Model):
    _name = 'hr.manual.attendance'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    get_hr_att_id_check_in_row_query = """SELECT id FROM hr_attendance
                                      WHERE employee_id = %s AND
                                      check_in < %s AND
                                      check_out IS NULL
                                      ORDER BY check_in DESC LIMIT 1"""

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.multi
    def _default_approver(self):
        default_approver = 0
        employee = self._default_employee()
        if isinstance(employee, int):
            emp_obj = self.env['hr.employee'].search([('id', '=', employee)], limit=1)
            if emp_obj.sudo().holidays_approvers:
                default_approver = emp_obj.sudo().holidays_approvers[0].approver.id
        else:
            if employee.sudo().holidays_approvers:
                default_approver = employee.sudo().holidays_approvers[0].approver.id
        return default_approver

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, default=_default_employee)
    reason = fields.Text(string='Reason')
    is_it_official = fields.Boolean(string='Is it official', default=False)
    check_in = fields.Datetime(string = 'Check In',track_visibility='onchange')
    check_out = fields.Datetime(string = 'Check out',track_visibility='onchange')
    sign_type = fields.Selection([
        ('both', 'Both'),
        ('sign_in', 'Sign In'),
        ('sign_out', 'Sign Out')
        ], string = 'Sign Type',track_visibility='onchange', required=True, default="both")
    department_id = fields.Many2one('hr.department', related='employee_id.department_id',
                                    string='Department', store=True)
    manager_id = fields.Many2one('hr.employee', string='Employee Manager',
                                 related='employee_id.parent_id')
    approver_id = fields.Many2one('res.users', string='Approvar', readonly=True, copy=False,
                                  help='This field is automatically filled by the user who validate the manual attendance request')
    my_menu_check = fields.Boolean(string='Check',readonly=True)
    # check_error = fields.Boolean(string='Check Error',readonly=True, default=False )
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True,
                              default=lambda self: self.env.uid, readonly=True)
    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True,
                                       default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
                                            related='pending_approver.user_id', related_sudo=True, store=True,
                                            readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    approbations_ids = fields.One2many('hr.employee.manual.att.approbation', 'manual_attandance_id', string='Approvals', readonly=True)

    parent_id = fields.Many2one('hr.manual.attendance.batches',ondelete="cascade")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a manual attendance request is created." +
             "\nThe status is 'To Approve', when manual attendance request is confirmed by user." +
             "\nThe status is 'Refused', when manual attendance request is refused by manager." +
             "\nThe status is 'Approved', when manual attendance request is approved by manager.")


    ####################################################
    # Business methods
    ####################################################

    def getDateTimeFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        else:
            return None

    @api.multi
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    @api.onchange('sign_type')
    def orientation_details(self):
        self.check_in = False
        self.check_out = False

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id and self.employee_id.holidays_approvers:
            self.pending_approver = self.employee_id.holidays_approvers[0].approver.id
        else:
            self.pending_approver = False

    @api.one
    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id:
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False

    @api.multi
    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request or if he is a Manager."""
        user = self.env.user
        group_hr_manager = self.env.ref('hr_attendance.group_hr_attendance_user')
        for att in self:
            if group_hr_manager in user.groups_id or att.employee_id and att.employee_id.user_id == user:
                att.can_reset = True

    @api.multi
    def action_confirm(self):
        if self.filtered(lambda manual_attendance: manual_attendance.state != 'draft'):
            raise UserError(_('Manual Attendance request must be in Draft state ("To Submit") in order to confirm it.'))
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        for manual_attendance in self:
            if manual_attendance.state != 'confirm':
                raise UserError(_('Manual Attendance Request must be confirmed ("To Approve") in order to approve it.'))
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in manual_attendance.employee_id.holidays_approvers:
                sequence = sequence + 1
                if manual_attendance.pending_approver.id == approver.approver.id:
                    if sequence == len(manual_attendance.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = manual_attendance.employee_id.holidays_approvers[sequence].approver
            if is_last_approbation:
                manual_attendance.action_validate()
            else:
                vals = {'state': 'confirm'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                manual_attendance.write(vals)
                self.env['hr.employee.manual.att.approbation'].create(
                    {'manual_attandance_id': manual_attendance.id, 'approver': self.env.uid, 'sequence': sequence,
                     'date': fields.Datetime.now()})

    @api.multi
    def action_validate(self):
        ### Here Only Both Type is Implemented as other type not implemented properly;
        ### I blocked that part : Matiar Rahman
        attendance_obj = self.env['hr.attendance']
        for manual_attendance in self:
            if manual_attendance.state not in ['confirm']:
                raise UserError(_('Manual Attendance request must be confirmed in order to approve it.'))
            vals1 = {}
            vals1['employee_id'] = manual_attendance.employee_id.id
            vals1['operating_unit_id'] = manual_attendance.employee_id.operating_unit_id.id
            vals1['manual_attendance_request'] = True

            if manual_attendance.sign_type == 'both':
                vals1['check_in'] = manual_attendance.check_in
                vals1['check_out'] = manual_attendance.check_out
                attendance_obj.create(vals1)
            elif manual_attendance.sign_type == 'sign_in':
                vals1['check_in'] = manual_attendance.check_in
                hr_att_pool = self.env['hr.attendance']
                preAttData = hr_att_pool.search([('employee_id', '=', manual_attendance.employee_id.id),
                                                 ('check_out', '>', manual_attendance.check_in),
                                                 ('check_in', '=', False)], limit=1, order='check_out asc')
                if preAttData:
                    timeDiffInHrs = (self.getDateTimeFromStr(preAttData.check_out) - self.getDateTimeFromStr(manual_attendance.check_in)).total_seconds() / 60 / 60
                    if timeDiffInHrs <= 15:
                        preAttData.write({'check_in': manual_attendance.check_in})
                    else:
                        attendance_obj.create(vals1)
                else:
                    attendance_obj.create(vals1)

            elif manual_attendance.sign_type == 'sign_out':
                vals1['check_out'] = manual_attendance.check_out

                hr_att_pool = self.env['hr.attendance']
                preAttData = hr_att_pool.search([('employee_id', '=', manual_attendance.employee_id.id),
                                                 ('check_in', '<', manual_attendance.check_out),
                                                 ('check_out', '=', False)], limit=1, order='check_in desc')
                if preAttData:
                    timeDiffInHrs = (self.getDateTimeFromStr(manual_attendance.check_out) - self.getDateTimeFromStr(preAttData.check_in)).total_seconds() / 60 / 60
                    if timeDiffInHrs <= 15:
                        preAttData.write({'check_out': manual_attendance.check_out})
                    else:
                        attendance_obj.create(vals1)
                else:
                    attendance_obj.create(vals1)
            manual_attendance.write({'state': 'validate'})

    @api.multi
    def action_refuse(self):
        for manual_attendance in self:
            if self.state not in ['confirm','validate']:
                raise UserError(_('Manual Attendance request must be confirmed or validated in order to refuse it.'))
            manual_attendance.write({'state': 'refuse'})
        return True

    @api.multi
    def action_draft(self):
        for att in self:
            self.write({
                'state': 'draft',
            })
        return True

    ####################################################
    # Override methods
    ####################################################

    @api.model
    def create(self, vals):
        if vals.get('employee_id', False):
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if employee and employee.holidays_approvers and employee.holidays_approvers[0]:
                vals['pending_approver'] = employee.holidays_approvers[0].approver.id
        res = super(HrManualAttendance, self).create(vals)
        res._notify_approvers()
        return res

    @api.multi
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if employee_id:
            self.pending_approver = self.env['hr.employee'].search([('id', '=', employee_id)]).holidays_approvers[0].approver.id
        res = super(HrManualAttendance, self).write(values)
        return res

    @api.multi
    def unlink(self):
        for m in self:
            if m.state != 'draft':
                raise UserError(_('You can not delete this.'))
        return super(HrManualAttendance, self).unlink()

    ### mail notification
    @api.multi
    def _notify_approvers(self):
        approvers = self.employee_id._get_employee_manager()
        if not approvers:
            return True
        for approver in approvers:
            self.sudo(SUPERUSER_ID).add_follower(approver.id)
            if approver.sudo(SUPERUSER_ID).user_id:
                self.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
                    [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        return True



    @api.depends('employee_id')
    @api.onchange('employee_id')
    def onchange_employee(self):
        for recode in self:
            if recode.parent_id.employee_id:
                recode.employee_id = recode.parent_id.employee_id.id
                recode.department_id = recode.parent_id.department_id.id

    @api.constrains('check_in', 'check_out')
    def _check_value(self):
        if self.sign_type == "both":
            deff = (self.getDateTimeFromStr(self.check_out) - self.getDateTimeFromStr(
                self.check_in)).total_seconds() / 60 / 60
            if self.check_in >= self.check_out:
                raise UserError(_("Check out time must be greater than check in time!"))
            elif self.check_in > datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"):
                raise UserError(_("Check in time must be less than current time!"))
            elif deff > 13:
                raise UserError(_("Difference between check in time and check out time duration must be upto 13 hours!"))
        elif self.sign_type == "sign_in":
            if self.check_in > datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"):
                raise UserError(_("Check in time must be less than current time!"))

        elif self.sign_type == "sign_out":
           if self.check_out > datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"):
                raise UserError(_("Check out time must be less than current time!"))

    @api.constrains('check_in', 'check_out')
    def _check_time(self):
        sl_pool = self.env["hr.short.leave"]
        att_pool = self.env["hr.attendance"]
        for h in self:
            domain = [
                ('check_in', '<', h.check_out),
                ('check_out', '>', h.check_in),
                ('employee_id', '=', h.employee_id.id),
                ('id', '!=', h.id),
                ('state', 'not in', ['cancel', 'refuse']),
                #('check_error', '=', h.write({'check_error': True})),
            ]
            sl_domain = [
                ('date_from', '<', h.check_out),
                ('date_to', '>', h.check_in),
                ('employee_id', '=', h.employee_id.id),
                ('id', '!=', h.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            att_domain =[
                ('check_in', '<', h.check_out),
                ('check_out', '>', h.check_in),
                ('employee_id', '=', h.employee_id.id),
                ('id', '!=', h.id),
            ]
            check_manual_att = self.search_count(domain)
            if check_manual_att:
                #self.write({'check_error': True})
                # datetime.datetime.strptime(dateStr, "%Y-%m-%d")
                date_time_check_in =  datetime.datetime.strptime(h.check_in, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=6)
                date_time_check_out =  datetime.datetime.strptime(h.check_out, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=6)
                raise ValidationError(_(" The duration of the period  (%s)  and  (%s)  are overlapping with existing Manual Attendance ." %(date_time_check_in,date_time_check_out)
                                        ))


            check_sl = sl_pool.search_count(sl_domain)
            if check_sl:
                date_time_check_in = datetime.datetime.strptime(h.check_in, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=6)
                date_time_check_out = datetime.datetime.strptime(h.check_out, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=6)
                raise ValidationError(_(" The duration of the period  (%s)  and  (%s)  are overlapping with existing Short Leave ." %(date_time_check_in,date_time_check_out)
                                        ))

            check_att = att_pool.search_count(att_domain)
            if check_att:
                date_time_check_in = datetime.datetime.strptime(h.check_in, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=6)
                date_time_check_out = datetime.datetime.strptime(h.check_out, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=6)
                raise ValidationError(_("The duration of the period  (%s)  and  (%s)  are overlapping with existing Attendance ." %(date_time_check_in,date_time_check_out)
                                        ))

