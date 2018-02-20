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
                                                 ('check_in', '=', False)], limit=1, order='check_in desc')
                if preAttData:
                    timeDiffInHrs = (self.getDateTimeFromStr(manual_attendance.check_out) - self.getDateTimeFromStr(preAttData.check_in)).total_seconds() / 60 / 60
                    if timeDiffInHrs <= 15:
                        preAttData.write({'check_out': manual_attendance.check_out})
                    else:
                        attendance_obj.create(vals1)
                else:
                    attendance_obj.create(vals1)
            manual_attendance.write({'state': 'validate'})

    @api.constrains('check_in', 'check_in')
    def _check_value(self):
        deff= (self.getDateTimeFromStr(self.check_out) - self.getDateTimeFromStr(self.check_in)).total_seconds() / 60 / 60
        if self.check_in >= self.check_out:
            raise Warning("[Error] Check out must be greater than check in!")

        elif deff >= 9:
            raise Warning("[Error] Difference between check in and check out must be upto 9 hours")
