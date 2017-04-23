from openerp import models, fields
from openerp import api

class AttendanceErrorCorrection(models.TransientModel):
    _name = 'hr.attendance.error.correction'

    _description = 'HR attendance error correction'

    type = fields.Selection([
        ('department_type', 'Department wise'),
        ('employee_type', 'Employee wise')
    ], string='Type', required=True)

    department_id = fields.Many2one("hr.department", string="Department", required=False)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=False)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)

    @api.multi
    def search_data(self):

        view = self.env.ref('gbs_hr_attendance_error_correction.hr_attendance_error_tree')
        employee_pool = self.env['hr.employee']
        attendance_pool = self.env['hr.attendance']

        if(self.type == 'department_type'):

            emp_ids = employee_pool.search([('department_id', '=', self.department_id.id)])
            att_ids = attendance_pool.search(['&',
                                              '&', ('has_error', '=', True), ('employee_id', 'in', emp_ids.ids),
                                              '|', '&', ('check_in', '>=', self.from_date),
                                              ('check_in', '<=', self.to_date),
                                              '&', ('check_out', '>=', self.from_date),
                                              ('check_out', '<=', self.to_date)])

            return {
                'name': ('Error Data'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'hr.attendance',
                'domain': [('id', '=', att_ids.ids)],
                'view_id': [view.id],
                'type': 'ir.actions.act_window'
            }

        elif(self.type == 'employee_type'):
            att_ids = attendance_pool.search(['&',
                                              '&',('has_error', '=', True), ('employee_id', '=', self.employee_id.id),
                                              '|', '&', ('check_in', '>=', self.from_date), ('check_in', '<=', self.to_date),
                                               '&', ('check_out', '>=', self.from_date), ('check_out', '<=', self.to_date)])

            return {
                'name': ('Error Data'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'hr.attendance',
                'domain': [('id','=',att_ids.ids)],
                'view_id': [view.id],
                'type': 'ir.actions.act_window'
            }