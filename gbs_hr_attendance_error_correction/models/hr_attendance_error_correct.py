from openerp import api, fields, models

class AttendanceErrorCorrect(models.Model):
    _name = 'hr.attendance.error.correct'

    _description = 'HR attendance error correct'

    type = fields.Selection([
        ('department_type', 'Department wise'),
        ('employee_type', 'Employee wise')
    ], string='Type', required=True)

    department_name = fields.Many2one("hr.department", string="Department", required=False)
    employee_name = fields.Many2one("hr.employee", string="Employee", required=False)
    from_date = fields.Datetime(string='From Date', required=True)
    to_date = fields.Datetime(string='To Date', required=True)
    attendance_line_ids = fields.One2many('hr.attendance', 'employee_id', domain=[('has_error', '=', True)])

    @api.constrains('from_date', 'to_date')
    def generate_filtered_data(self):
        datas = self.env['hr.attendance'].search([('check_in', '>=', self.from_date), ('check_out', '<=', self.to_date)])

        for data in datas:
            print "=Employee Name=", data.employee_id.id
            print "=Employee Check In=", data.check_in
            print "=Employee Check Out=", data.check_out