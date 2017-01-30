from openerp import api
from openerp import fields
from openerp import models
from duplicity.tempdir import default
from odoo.exceptions import UserError

from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import ValidationError,Warning



class HrManualAttendance(models.Model):
    _name = 'hr.manual.attendance'
    _inherit = ['mail.thread']

    #Fields of Model    
    name = fields.Char()
    reason = fields.Text(string='Reason')
    is_it_official = fields.Boolean(string='Is it official', default=False)
    check_in_time_full_day = fields.Date(string = 'Check In time full day')
    check_out_time_full_day = fields.Date(string = 'Check out time full day')    
    check_in_time_sign_in = fields.Date(string = 'Check In time Sign In')
    check_in_time_sign_out = fields.Date(string = 'Check Out time Sign Out')    
    sign_type = fields.Selection([
        ('full_day', 'Full Day'),
        ('sign_in', 'Sign In'),
        ('sign_out', 'Sign Out')
        ], string = 'Sign Type')    
    employee_id = fields.Many2one('hr.employee', string="Employee", required = True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True)   
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
            help="The status is set to 'To Submit', when a manual attendance request is created." +
            "\nThe status is 'To Approve', when manual attendance request is confirmed by user." +
            "\nThe status is 'Refused', when manual attendance request is refused by manager." +
            "\nThe status is 'Approved', when manual attendance request is approved by manager.")    
    manager_id = fields.Many2one('hr.employee', string='Final Approval', readonly=True, copy=False,
        help='This area is automatically filled by the user who validate the manual attendance request')    
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
    def _validity_check_in_check_out_manual_attendances11(self):
                
        check_in_time_full_day = self.check_in_time_full_day        
        check_out_time_full_day = self.check_out_time_full_day - datetime.now().date()
        
        check_in_time_sign_in = self.check_in_time_sign_in - datetime.now().date()
        check_in_time_sign_out = self.check_in_time_sign_out - datetime.now().date()
        
        min_days_obj = self.env['hr.manual.attendance.min.days']
        
        min_day_restriction_config = min_days_obj.min_days_restriction
        
        if check_out_time_full_day > min_day_restriction_config: 
            raise ValidationError(_('Minimum days of requesting manual attendance is over'))
        if check_in_time_sign_in > min_day_restriction_config: 
            raise ValidationError(_('Minimum days of requesting manual attendance is over'))
        if check_in_time_sign_out > min_day_restriction_config: 
            raise ValidationError(_('Minimum days of requesting manual attendance is over'))
                
        for attendance in self:
            if datetime.strptime(attendance.check_in_time_full_day, DEFAULT_SERVER_DATE_FORMAT).date() > datetime.now().date():
                raise ValidationError(_('"Check In" time cannot be future date'))
            
            if datetime.strptime(attendance.check_out_time_full_day, DEFAULT_SERVER_DATE_FORMAT).date() > datetime.now().date():
                raise ValidationError(_('"Check out" time cannot be future date'))
          
            if datetime.strptime(attendance.check_in_time_sign_in, DEFAULT_SERVER_DATE_FORMAT).date() > datetime.now().date():
                raise ValidationError(_('"Check In" time cannot be future date'))
            
            if datetime.strptime(attendance.check_in_time_sign_out, DEFAULT_SERVER_DATE_FORMAT).date() > datetime.now().date():
                raise ValidationError(_('"Check In" time cannot be future date'))
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
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only Manager can approve Manual Attendance Request.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for manual_attendance in self:
            if manual_attendance.state != 'confirm':
                raise UserError(_('Manual Attendance Request must be confirmed ("To Approve") in order to approve it.'))

            manual_attendance.action_validate()
    
    @api.multi
    def action_validate(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for manual_attendance in self:
            if manual_attendance.state not in ['confirm', 'validate1']:
                raise UserError(_('Manual Attendance request must be confirmed in order to approve it.'))
            if manual_attendance.state == 'validate' and not manual_attendance.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only Manager can apply the approval on manual attendance requests.'))
            
            manual_attendance.write({ 'state': 'validate', 'manager_id':manager.id})
            
        
            ## Update HR Attendance Table
        attendance_obj = self.env['hr.attendance']
        manual_attendace_ob = self.env['hr.manual.attendance'].search([('employee_id', '=', manual_attendance.employee_id.id)]) 
            
        vals1 = {}
        
        for mab in manual_attendace_ob:
              
            vals1['employee_id'] = mab.employee_id.id
            
            if mab.check_in_time_full_day: 
                vals1['check_in'] = mab.check_in_time_full_day
            elif mab.check_in_time_sign_in: 
                vals1['check_in'] = mab.check_in_time_sign_in
                
            if mab.check_out_time_full_day:
                vals1['check_out'] = mab.check_out_time_full_day
            elif mab.check_in_time_sign_out:    
                vals1['check_out'] = mab.check_in_time_sign_out

            vals1['manual_attendance_request'] = True
                
            attendance_obj.create(vals1)
         
        attendance_obj2 = self.env['hr.attendance'].search([('employee_id', '=', manual_attendance.employee_id.id)])    
        
        valr = {}
        
        for att in attendance_obj2:
            for a in self:
                if att.check_in and a.check_in_time_full_day:
                    valr['check_in'] = a.check_in_time_full_day
            
                if att.check_in and a.check_in_time_sign_in:
                    valr['check_in'] = a.check_in_time_sign_in    
                
            attendance_obj2.write(valr)
       
        return True
    
    
    @api.multi
    def action_refuse(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only Manager can refuse Manual Attendance requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for manual_attendance in self:
            if self.state not in ['confirm','validate']:
                raise UserError(_('Manual Attendance request must be confirmed or validated in order to refuse it.'))

            manual_attendance.write({'state': 'refuse', 'manager_id': manager.id})
                        
        return True
    
    
    @api.multi
    def action_draft(self):
        for holiday in self:
            if not holiday.can_reset:
                raise UserError(_('Only Manager or the concerned employee can reset to draft.'))
            if holiday.state not in ['confirm', 'refuse']:
                raise UserError(_('Manual attendance request state must be "Refused" or "To Approve" in order to reset to Draft.'))
            holiday.write({
                'state': 'draft',
                'manager_id': False                
            })
            
        return True
    
