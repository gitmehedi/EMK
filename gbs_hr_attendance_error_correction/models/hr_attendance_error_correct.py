from openerp import models, fields
from openerp import api

class AttendanceErrorCorrect(models.Model):
    _name = 'hr.attendance.error.correct'

    _description = 'HR attendance error correct'

    type = fields.Selection([
        ('department_type', 'Department wise'),
        ('employee_type', 'Employee wise')
    ], string='Type', required=True)

    department_name = fields.Many2one("hr.department", string="Department", required=False)
    employee_name = fields.Many2one("hr.employee", string="Employee", required=False)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)

    #attendance_line_ids = fields.One2many('hr.attendance', 'employee_id', domain=[('has_error', '=', True)])

    @api.multi
    @api.constrains('department_name', 'employee_name', 'from_date', 'to_date')
    def generate_filtered_data(self):
        #domain = []
        if self.type == 'department_type':
            employees = self.env['hr.employee'].search([('department_id', '=', self.department_name.id)])

            for emp in employees:
                attendances = self.env['hr.attendance'].search([('has_error', '=', True), ('employee_id', '=', emp.id),
                                                                ('create_date', '>=', self.from_date), ('create_date', '<=', self.to_date)])
                for att in attendances:
                    #domain.append([att.id, att.check_in, att.check_out])
                    print "=====Departmentwise Attendances", att.id

        elif self.type == 'employee_type':
            attendances = self.env['hr.attendance'].search([('has_error', '=', True), ('employee_id', '=', self.employee_name.id),
                                                            ('create_date', '>=', self.from_date), ('create_date', '<=', self.to_date)])
            for att in attendances:
                #domain.append([att.id, att.check_in, att.check_out])
                print "=====Employeetwise Attendances", att.id

        return {
            'name': 'Error Data',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            #'src_model': 'hr.attendance',
            'res_model': 'hr.attendance',
            'target': 'current',
            'domain': [('employee_id', '=', 'hr_employee_al')],
            'view_id': False,
            #'res_id': att.id,
            'nodestroy': False
        }