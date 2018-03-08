from odoo import api, fields, models, _

class AttErrorSummary(models.TransientModel):
    _name = 'hr.overtime.summary.wizard'
    _description = 'Overtime Summary Report'


    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    emp_id = fields.Many2one('hr.employee', string='Employee Name', required=True)

    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        if self.operating_unit_id:
            self.emp_id = []
            return {'domain': {'emp_id': [('operating_unit_id', '=', self.operating_unit_id.id)]}}

    @api.multi
    def process_report(self):
        data = {}
        data['emp_id'] = self.emp_id.id
        data['emp_name'] = self.emp_id.name
        data['emp_department_id'] = self.emp_id.department_id.id
        data['emp_department_name'] = self.emp_id.department_id.name
        data['emp_job_id'] = self.emp_id.job_id.id
        data['emp_job_name'] = self.emp_id.job_id.name
        data['device_no'] = self.emp_id.device_employee_acc
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name

        return self.env['report'].get_action(self, 'hr_overtime_report.overtime_summary_report', data=data)


