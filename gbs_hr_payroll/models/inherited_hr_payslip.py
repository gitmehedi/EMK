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

        absent_days = None
        if len(periods)>0:
            id = periods
        else:
            id = 0
        emp_data = self.env['hr.attendance.summary'].search([('period', '=', id)])

        obj = self.env['hr.payslip.worked_days']
        # for emp in emp_data:
        #     if self.employee_id == emp.employee_id:

        worked_days_lines = self.worked_days_line_ids
        if self.worked_days_line_ids:
            worked_days_lines += worked_days_lines.new({
                'code': 'Absent',
                'contract_id': self.contract_id.id,
                'number_of_days': 5,
                'name': 'Absent',
                'payslip_id': 1,

            })
        self.worked_days_line_ids = worked_days_lines




