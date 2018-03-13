from odoo import api, fields, models, tools, _


class InheritedHrAttendancePayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on 
    employee_id
    """
    _inherit = "hr.payslip"

    @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):

        res = super(InheritedHrAttendancePayslip, self).onchange_employee_id(date_from,
                                                                             date_to,
                                                                             employee_id,
                                                                             contract_id)

        if self.employee_id:
            self.worked_days_line_ids = 0

            """
            Insert attendance data
            """
            periods = self.env['account.period'].search(
                [('date_start', '<=', self.date_from), ('date_stop', '>=', self.date_to)], limit=1)

            if periods.id == False:
                return

            summary_data = self.env['hr.attendance.summary'].search([('period', '=', periods.id),
                                                 ('state', '=', 'approved'),
                                                 ('operating_unit_id', '=', self.employee_id.operating_unit_id.id)], limit=1)

            if summary_data.id == False:
                return

            summary_line_data = self.env['hr.attendance.summary.line'].search([('att_summary_id', '=', summary_data.id),
                                                                     ('employee_id', '=', self.employee_id.id)], limit=1)


            if summary_line_data.id == False:
                return

            worked_days_lines = self.worked_days_line_ids
            if summary_line_data.leave_days:
                worked_days_lines += worked_days_lines.new({
                    'code': 'LEAVE',
                    'contract_id': self.contract_id.id,
                    'number_of_days': summary_line_data.leave_days,
                    'name': 'Leave Days',
                })
            if summary_line_data.cal_ot_hrs:
                worked_days_lines += worked_days_lines.new({
                    'code': 'OT',
                    'contract_id': self.contract_id.id,
                    'number_of_hours': summary_line_data.cal_ot_hrs,
                    'name': 'OT Hours',
                })

            ### Late Deduction Days
            if summary_line_data.deduction_days >= 0:
                worked_days_lines += worked_days_lines.new({
                    'code': 'LDD',
                    'contract_id': self.contract_id.id,
                    'number_of_days': summary_line_data.deduction_days or 0,
                    'name': 'Late Deduction Day(s)',
                })
            self.worked_days_line_ids = worked_days_lines

            ### ABS Deduction Days
            if summary_line_data.absent_count >= 0:
                worked_days_lines += worked_days_lines.new({
                    'code': 'ABS',
                    'contract_id': self.contract_id.id,
                    'number_of_days': summary_line_data.absent_count or 0,
                    'name': 'ABS Deduction Day(s)',
                })
            self.worked_days_line_ids = worked_days_lines








