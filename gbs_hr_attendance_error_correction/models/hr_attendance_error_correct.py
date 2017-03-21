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
    attendance_line_ids = fields.One2many('hr.attendance', 'employee_id', string='Employee Attendances')

    """invoice_line_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines',
                                       oldname='invoice_line',
                                       readonly=True, states={'draft': [('readonly', False)]}, copy=True)"""