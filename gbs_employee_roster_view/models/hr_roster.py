from odoo import api,fields, models

class EmpRoster(models.TransientModel):

        _name = 'hr.emp.roster'
        _description = 'Employee Roster'

        type = fields.Selection([
            ('op_type', 'Operating Unit wise'),
            ('department_type', 'Department wise'),
            ('employee_type', 'Employee wise')
        ], string='Type', required=True)

        operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit', required=True,
                                            default=lambda self: self.env.user.default_operating_unit_id)

        department_id = fields.Many2one("hr.department", string="Department", required=False)
        employee_id = fields.Many2one("hr.employee", string="Employee", required=False)
        from_date = fields.Date(string='From Date', required=True)
        to_date = fields.Date(string='To Date', required=True)
