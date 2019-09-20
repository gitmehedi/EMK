from odoo import models, fields, api, _

class HrLeaveCarryForwardtLine(models.Model):
    _name = 'hr.leave.forward.encash.line'
    _description = 'HR save carry forward line'
    _rec_name = 'carry_forward_year'
    _inherit = ['mail.thread']

    authorized_leave = fields.Integer(string="Authorized", readonly=True)
    availed_leave = fields.Integer(string="Availed", readonly=True)
    balance_leave = fields.Integer(string="Balance", readonly=True)

    encashment_leave = fields.Integer(string="Encashment", track_visibility='onchange')
    carried_leave = fields.Integer(string="Carried Over", track_visibility='onchange')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved")
    ], default='draft', track_visibility='onchange')


    parent_id = fields.Many2one('hr.leave.forward.encash', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee ID",ondelete='cascade')

    emp_name = fields.Char(size=100, string='Name', related='employee_id.name', readonly=True)
    department_name = fields.Char(related='employee_id.department_id.name', string='Department', readonly=True)
    designation_name = fields.Char(related='employee_id.job_id.name', string='Designation', readonly=True)
    date_of_join = fields.Date(related='employee_id.initial_employment_date', string='Date Of Join', readonly=True)
    acc_no = fields.Integer(related='employee_id.device_employee_acc', string='Employee ID', readonly=True)
    carry_forward_year = fields.Char(related='parent_id.carry_forward_year.name', string='Encashment Year', readonly=True)
    leave_type = fields.Char(string='Leave Type', related='parent_id.leave_type.name', readonly=True)

    pay_status = fields.Boolean(string ='Pay', default=False, help='Employee Received the Payment.')

    @api.multi
    def action_confirm(self):
        res = self.env.ref('gbs_hr_leave_forward_encash.my_leave_confirm_wizard')
        result = {
            'name': _('Please Enter The Request'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'my.leave.confirm.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result