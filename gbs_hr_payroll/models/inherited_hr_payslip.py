from odoo import api, fields, models, tools, _


class InheritedHrPayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on 
    employee_id
    """
    _inherit = "hr.payslip"

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        self.contract_id = 0
        self.struct_id = 0
        self.worked_days_line_ids = 0
        super(InheritedHrPayslip, self).onchange_employee()
        periods = self.env['account.period'].search([('date_start','<=',self.date_from),('date_stop','>=',self.date_to)], limit=1)

        id = periods.id if len(periods) > 0 else 0
        emp_data = self.env['hr.attendance.summary'].search([('period', '=', id)])

        worked_days_lines = self.worked_days_line_ids
        for emp in emp_data.att_summary_lines:
            if self.employee_id == emp.employee_id:

                if emp.leave_days:
                    if self.worked_days_line_ids:
                        worked_days_lines += worked_days_lines.new({
                            'code': 'Leave',
                            'contract_id': self.contract_id.id,
                            'number_of_days': emp.leave_days,
                            'name': 'Leave Days',
                        })
                if emp.cal_ot_hrs:
                    if self.worked_days_line_ids:
                        worked_days_lines += worked_days_lines.new({
                            'code': 'OT',
                            'contract_id': self.contract_id.id,
                            'number_of_hours': emp.cal_ot_hrs,
                            'name': 'OT Hours',
                        })
                if emp.late_hrs:
                    if self.worked_days_line_ids:
                        worked_days_lines += worked_days_lines.new({
                            'code': 'Late',
                            'contract_id': self.contract_id.id,
                            'number_of_hours': emp.late_hrs,
                            'name': 'Late Hours',
                        })
                self.worked_days_line_ids = worked_days_lines




