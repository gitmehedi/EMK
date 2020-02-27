from odoo import api, fields, models, tools, _

class InheritedHrAttendancePayslip(models.Model):
    _inherit = "hr.payslip"

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if self.employee_id:
            holiday_allowance_data = self.env['hr.holiday.allowance.line'].search([('emp_allowance_date', '>=', self.date_from),
                                                                                   ('emp_allowance_date', '<=', self.date_to),
                                                                                   ('state', '=', 'approved'),
                                                                                   ('employee_id', '=', self.employee_id.id)])
            worked_days_lines = self.worked_days_line_ids
            if len(holiday_allowance_data)>0:
                worked_days_lines += worked_days_lines.new({
                    'code': 'HALW',
                    'contract_id': self.contract_id.id,
                    'number_of_days': len(holiday_allowance_data),
                    'name': 'Holiday Allowance Days'
                })
            self.worked_days_line_ids = worked_days_lines