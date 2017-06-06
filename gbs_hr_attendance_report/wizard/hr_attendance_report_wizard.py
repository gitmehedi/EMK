from openerp import models, fields, api


class HrBankSelectionWizard(models.TransientModel):
    _name = 'hr.attendance.report.wizard'

    check_in_out = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ], string = 'Check Type', required=True, default="check_in")

    type = fields.Selection([
        ('department_type', 'Department wise'),
        ('employee_type', 'Employee wise')
    ], string='Type', required=True)

    department_id = fields.Many2one("hr.department", string="Department", required=False)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=False)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)

    @api.multi
    def process_report(self):
        print 'Hello! Report!!'