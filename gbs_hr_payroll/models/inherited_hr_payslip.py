from odoo import api, fields, models, tools, _


class InheritedHrPayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on 
    employee_id
    """
    _inherit = "hr.payslip"

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.contract_id = 0
            self.struct_id = 0
            self.worked_days_line_ids = 0
            self.input_line_ids = 0
            super(InheritedHrPayslip, self).onchange_employee()


            """
            Insert attendance data
            """
            periods = self.env['account.period'].search([('date_start','<=',self.date_from),('date_stop','>=',self.date_to)], limit=1)
            emp_data = self.env['hr.attendance.summary'].search([('period', '=', periods.id if len(periods) > 0 else 0)])

            if emp_data:
                worked_days_lines = self.worked_days_line_ids
                for emp in emp_data.att_summary_lines:
                    if self.employee_id == emp.employee_id:

                        if emp.leave_days:
                            worked_days_lines += worked_days_lines.new({
                                'code': 'LEAVE',
                                'contract_id': self.contract_id.id,
                                'number_of_days': emp.leave_days,
                                'name': 'Leave Days',
                            })
                        if emp.cal_ot_hrs:
                            worked_days_lines += worked_days_lines.new({
                                'code': 'OT',
                                'contract_id': self.contract_id.id,
                                'number_of_hours': emp.cal_ot_hrs,
                                'name': 'OT Hours',
                            })
                        if emp.late_hrs:
                            worked_days_lines += worked_days_lines.new({
                                'code': 'LATE',
                                'contract_id': self.contract_id.id,
                                'number_of_hours': emp.late_hrs,
                                'name': 'Late Hours',
                            })
                        self.worked_days_line_ids = worked_days_lines


            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            loan_data = self.env['hr.employee.loan.line'].search([('employee_id', '=', self.employee_id.id),
                                                                  ('schedule_date', '>=', self.date_from),
                                                                  ('schedule_date', '<=', self.date_to),
                                                                  ('state', '=', 'pending')], limit=1)
            mobile_data = self.env['hr.mobile.bill.line'].search([('employee_id', '=', self.employee_id.id)], limit=1)
            meal_data = self.env['hr.meal.bill.line'].search([('employee_id', '=', self.employee_id.id)], limit=1)

            """
            Loan Data
            """
            if loan_data and self.contract_id.id:
                other_line_ids += other_line_ids.new({
                    'name': 'Current Loan',
                    'code': "LOAN",
                    'amount': loan_data.installment,
                    'contract_id': self.contract_id.id,
                })

            """
            Mobile Bills
            """
            if mobile_data and self.contract_id.id:
               other_line_ids += other_line_ids.new({
                    'name': 'Mobile Bill',
                    'code': "MOBILE",
                    'amount': mobile_data.amount,
                    'contract_id': self.contract_id.id,
            })
            """
            Meal Bills
            """
            if meal_data and self.contract_id.id:
                other_line_ids += other_line_ids.new({
                    'name': 'Meal Bill',
                    'code': "MEAL",
                    'amount': meal_data.bill_amount,
                    'contract_id': self.contract_id.id,
                })


            self.input_line_ids = other_line_ids


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        res = super(HrPayslipEmployees, self).compute_sheet()

        active_id = self.env.context.get('active_id')
        payslip_run = self.env['hr.payslip.run'].browse(active_id)

        for payslip in payslip_run.slip_ids:
            payslip.onchange_employee()

        return res

