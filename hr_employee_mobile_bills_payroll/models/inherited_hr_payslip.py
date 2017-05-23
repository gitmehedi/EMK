from odoo import api, fields, models, tools, _


class InheritedHrMobilePayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on 
    employee_id
    """
    _inherit = "hr.payslip"

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedHrMobilePayslip, self).onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            mobile_data = self.env['hr.mobile.bill.line'].search([('employee_id', '=', self.employee_id.id)], limit=1)

            """
            Mobile Bills
            """
            if mobile_data and self.contract_id.id and mobile_data.parent_id.state=='approved':
               other_line_ids += other_line_ids.new({
                    'name': 'Mobile Bill',
                    'code': "MOBILE",
                    'amount': mobile_data.amount,
                    'contract_id': self.contract_id.id,
            })
            self.input_line_ids = other_line_ids



