from odoo import api, fields, models, tools, _


class InheritedHrMobilePayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on 
    employee_id
    """
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.multi
    def action_payslip_done(self):
        res = super(InheritedHrMobilePayslip, self).action_payslip_done()

        mobile_ids = []
        for input in self.input_line_ids:
            if input.code == 'MOBILE':
                mobile_ids.append(int(input.ref))

        mobile_line_pool = self.env['hr.mobile.bill.line']
        mobile_data = mobile_line_pool.browse(mobile_ids)
        mobile_data.write({'state': 'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedHrMobilePayslip, self).onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            mobile_datas = self.env['hr.mobile.bill.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('state','=','approved')])

            """
            Mobile Bills
            """
            for mobile_data in mobile_datas:
               other_line_ids += other_line_ids.new({
                    'name': 'Mobile Bill',
                    'code': "MOBILE",
                    'amount': mobile_data.amount,
                    'contract_id': self.contract_id.id,
                    'ref': mobile_data.id,
            })
            self.input_line_ids = other_line_ids



