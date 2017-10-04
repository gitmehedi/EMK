from odoo import api, fields, models, tools, _

class InheritHRPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    ref = fields.Char('Reference')

    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHRPayslipInput, self).action_payslip_done()

        arrear_ids = []
        for input in self.input_line_ids:
            if input.code == 'ARREAR':
                arrear_ids.append(int(input.ref))

        arrear_line_pool = self.env['hr.payroll.arrear.line']
        arrear_data  = arrear_line_pool.browse(arrear_ids)
        arrear_data.write({'state':'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = 0
            super(InheritHRPayslipInput, self).onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            arrear_datas = self.env['hr.payroll.arrear.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('state','=','approved')])

            """
            Arrear Bills
            """
            for arrear_data in arrear_datas:
                other_line_ids += other_line_ids.new({
                    'name': 'Arrear',
                    'code': "ARREAR",
                    'amount': arrear_data.arear_amount,
                    'contract_id': self.contract_id.id,
                    'ref': arrear_data.id,
                })

            self.input_line_ids = other_line_ids