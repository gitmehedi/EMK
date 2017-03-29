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

    @api.constrains('department_name', 'employee_name', 'from_date', 'to_date')
    def generate_filtered_data(self):
        if self.type == 'department_type':
            # departments = self.env['hr.department'].search([('id', '=', self.department_name.id)])

            employees = self.env['hr.employee'].search([('department_id', '=', self.department_name.id)])

            for emp in employees:
                attendances = self.env['hr.attendance'].search([('has_error', '=', True), ('employee_id', '=', emp.id), ('check_in', '>=', self.from_date), ('check_out', '<=', self.to_date)])
                for att in attendances:
                    print "=====Attendance List=====", att.id

        elif self.type == 'employee_type':
            # employees = self.env['hr.employee'].search([('id', '=', self.employee_name.id)])

            attendances = self.env['hr.attendance'].search([('has_error', '=', True), ('employee_id', '=', self.employee_name.id), ('check_in', '>=', self.from_date), ('check_out', '<=', self.to_date)])

            for att in attendances:
                print "=====Attendance List=====", att.id


        '''for data in datas:
            print "=Employee Name=", data.employee_id.id
            print "=Employee Check In=", data.check_in
            print "=Employee Check Out=", data.check_out'''

        '''return {
            'view_type': 'tree',
            'view_mode': 'tree',
            'src_model': 'hr.attendance',
            'res_model': 'hr.attendance',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }'''