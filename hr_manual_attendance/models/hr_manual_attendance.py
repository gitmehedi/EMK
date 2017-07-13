from openerp import api
from openerp import models, fields,_
from openerp.exceptions import UserError, ValidationError

class HrManualAttendance(models.Model):
    _name = 'hr.manual.attendance'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, default=_default_employee)
    reason = fields.Text(string='Reason')
    is_it_official = fields.Boolean(string='Is it official', default=False)
    check_in = fields.Datetime(string = 'Check In')
    check_out = fields.Datetime(string = 'Check out')
    sign_type = fields.Selection([
        ('both', 'Both'),
        ('sign_in', 'Sign In'),
        ('sign_out', 'Sign Out')
        ], string = 'Sign Type', required=True, default="both")

    department_id = fields.Many2one('hr.department', related='employee_id.department_id',
                                    string='Department', store=True)
    manager_id = fields.Many2one('hr.employee', string='Employee Manager',
                                 related='employee_id.parent_id')
    approver_id = fields.Many2one('res.user', string='Approvar', readonly=True, copy=False,
                                  help='This field is automatically filled by the user who validate the manual attendance request')
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

    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')

    
    """
        This method does below things: 
        1. Check in/out date can not be a future date
        2. min day restriction of applying manual request
        **************************************************
        Basic functionality done, method has some known bugs. After 
        fixing it will be open to the application.
        
    """
    
    """
    @api.constrains('check_in_time_full_day', 'check_out_time_full_day', 'check_in_time_sign_in', 'check_in_time_sign_out')
    def _validity_check_in_check_out_manual_attendances(self):
       
        curr_date = datetime.date.today().strftime('%Y-%m-%d')
        
        if self.check_in_time_full_day > curr_date or self.check_in_time_sign_in > curr_date or self.check_in_time_sign_in > curr_date: 
            raise ValidationError(('"Check In" time cannot be future date'))       
        if self.check_out_time_full_day > curr_date:
            raise ValidationError(('"Check Out" time cannot be future date'))
        
        if self.check_in_time_full_day > self.check_out_time_full_day:
             raise ValidationError(('"Check In" cannot be greater than Check Out date'))
        
    
       
      #  Minimum days restriction apply


        min_days_obj = self.env['hr.manual.attendance.min.days'].search([('min_days_restriction', '=', 3)])

        ### Check in time full day min days restriction
        ck_sign_in_full = datetime.datetime.strptime(self.check_in_time_full_day, '%Y-%m-%d')
        current_date = datetime.datetime.strptime(curr_date, '%Y-%m-%d')
        start_date_check_in_full_day = date(ck_sign_in_full.year, ck_sign_in_full.month, ck_sign_in_full.day)
        end_date_check_in_full_day = date(current_date.year, current_date.month, current_date.day)
        delta = end_date_check_in_full_day - start_date_check_in_full_day

        if delta.days > min_days_obj.id:
            raise ValidationError(('You can not enter signin date of {} days ago'.format(delta)))

        ### Check in time full day min days restriction
        ck_sign_out_full = datetime.datetime.strptime(self.check_out_time_full_day, '%Y-%m-%d')
        current_date1 = datetime.datetime.strptime(curr_date, '%Y-%m-%d')
        start_date_check_in_full_day1 = date(ck_sign_out_full.year, ck_sign_out_full.month, ck_sign_out_full.day)
        end_date_check_in_full_day1 = date(current_date1.year, current_date1.month, current_date1.day)
        delta1 = end_date_check_in_full_day1 - start_date_check_in_full_day1

        if delta1.days > min_days_obj.id:
            raise ValidationError(('You can not enter signout date of {} days ago'.format(delta1)))

        ### Check in time full day min days restriction
        ck_sign_in = datetime.datetime.strptime(self.check_in_time_sign_in, '%Y-%m-%d')
        current_date2 = datetime.datetime.strptime(curr_date, '%Y-%m-%d')
        start_date_check_in_full_day2 = date(ck_sign_in.year, ck_sign_in.month, ck_sign_in.day)
        end_date_check_in_full_day2 = date(current_date2.year, current_date2.month, current_date2.day)
        delta2 = end_date_check_in_full_day2 - start_date_check_in_full_day2

        if delta2.days > min_days_obj.id:
            raise ValidationError(('You can not enter signin date of {} days ago'.format(delta2)))

        ### Check in time full day min days restriction
        ck_sign_in1 = datetime.datetime.strptime(self.check_in_time_sign_out, '%Y-%m-%d')
        current_date3 = datetime.datetime.strptime(curr_date, '%Y-%m-%d')
        start_date_check_in_full_day3 = date(ck_sign_in1.year, ck_sign_in1.month, ck_sign_in1.day)
        end_date_check_in_full_day3 = date(current_date3.year, current_date3.month, current_date3.day)
        delta3 = end_date_check_in_full_day3 - start_date_check_in_full_day3

        if delta3.days > min_days_obj.id:
            raise ValidationError(('You can not enter signout date of {} days ago'.format(delta3)))

    """
                  
    @api.multi
    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request
            or if he is a Manager.
        """
        user = self.env.user
        group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            if group_hr_manager in user.groups_id or holiday.employee_id and holiday.employee_id.user_id == user:
                holiday.can_reset = True
    
    @api.multi
    def action_confirm(self):
        if self.filtered(lambda manual_attendance: manual_attendance.state != 'draft'):
            raise UserError(_('Manual Attendance request must be in Draft state ("To Submit") in order to confirm it.'))
        return self.write({'state': 'confirm'})
    
    @api.multi
    def action_approve(self):
        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for manual_attendance in self:
            if manual_attendance.state != 'confirm':
                raise UserError(_('Manual Attendance Request must be confirmed ("To Approve") in order to approve it.'))

            manual_attendance.action_validate()
    
    @api.multi
    def action_validate(self):

        ### Here Only Both Type is Implemented as other type not implemented properly;
        ### I blocked that part : Matiar Rahman

        attendance_obj = self.env['hr.attendance']
        for manual_attendance in self:
            if manual_attendance.state not in ['confirm', 'validate1']:
                raise UserError(_('Manual Attendance request must be confirmed in order to approve it.'))
            if manual_attendance.state == 'validate' and not manual_attendance.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only Manager can apply the approval on manual attendance requests.'))

            vals1 = {}
            vals1['employee_id'] = manual_attendance.employee_id.id
            vals1['manual_attendance_request'] = True

            if manual_attendance.sign_type == 'both':
                vals1['check_in'] = manual_attendance.check_in
                vals1['check_out'] = manual_attendance.check_out
            elif manual_attendance.sign_type == 'sign_in':
                vals1['check_in'] = manual_attendance.check_in
            elif manual_attendance.sign_type == 'sign_out':
                vals1['check_out'] = manual_attendance.check_out

            attendance_obj.create(vals1)
            manual_attendance.write({'state': 'validate',
                                     'approver_id': self.env.uid})
         
        # attendance_obj2 = self.env['hr.attendance'].search([('employee_id', '=', manual_attendance.employee_id.id)])
        #
        # valr = {}
        #
        # for att in attendance_obj2:
        #     for a in self:
        #         if att.check_in and a.check_in:
        #             valr['check_in'] = a.check_in
        #
        #         if att.check_out and a.check_out:
        #             valr['check_out'] = a.check_out
        #
        #     attendance_obj2.write(valr)
       
        # return True
    
    @api.multi
    def action_refuse(self):
        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for manual_attendance in self:
            if self.state not in ['confirm','validate']:
                raise UserError(_('Manual Attendance request must be confirmed or validated in order to refuse it.'))

            manual_attendance.write({'state': 'refuse', 'manager_id': manager.id})
                        
        return True
    
    @api.multi
    def action_draft(self):
        for holiday in self:
            self.write({
                'state': 'draft',
                'manager_id': False                
            })
            
        return True

    # Show a msg for applied & approved state should not be delete
    @api.multi
    def unlink(self):
        for m in self:
            if m.state != 'draft':
                raise UserError(_('You can not delete this.'))
        return super(HrManualAttendance, self).unlink()
