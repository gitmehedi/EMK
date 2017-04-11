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
        print "==============Hello================="