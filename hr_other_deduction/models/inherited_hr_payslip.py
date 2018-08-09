from odoo import api, fields, models, tools, _

class InheritHRPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    ref = fields.Char('Reference')

class InheritHRPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHRPayslip, self).action_payslip_done()

        od_ids = []
        for input in self.input_line_ids:
            if input.code == 'ODS':
                od_ids.append(int(input.ref))

        od_line_pool = self.env['hr.other.deduction.line']
        od_data  = od_line_pool.browse(od_ids)
        od_data.write({'state':'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = 0
            super(InheritHRPayslip, self).onchange_employee()

            """
            Incorporate other payroll data
            """
            od_line_ids = self.input_line_ids
            od_datas = self.env['hr.other.deduction.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('state','=','approved')])


            for od_data in od_datas:
                od_line_ids += od_line_ids.new({
                    'name': 'Other Deduction',
                    'code': "ODS",
                    'amount': od_data.other_deduction_amount,
                    'contract_id': self.contract_id.id,
                    'ref': od_data.id,
                })

            self.input_line_ids = od_line_ids
