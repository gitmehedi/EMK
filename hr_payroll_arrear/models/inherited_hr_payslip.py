from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class InheritHRPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    ref = fields.Char('Reference')

    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHRPayslipInput, self).action_payslip_done()

        arrear_ids = []
        pay_slip_input = []
        for input in self.input_line_ids:
            if input.code == 'ARS':
                arrear_ids.append(int(input.ref))
                pay_slip_input.append(input.id)

        arrear_line_pool = self.env['hr.payroll.arrear.line']
        arrear_data = arrear_line_pool.browse(arrear_ids)
        if arrear_data.exists():
            arrear_data.write({'state':'adjusted'})
        elif len(arrear_ids) > 0:
            raise ValidationError(_("Arrear Data Error For: " + self.name + " hr_payslip_id :" + str(self.id) + ". Need to Update 'ref' from hr_pay_slip_input where id is :" + str(pay_slip_input)+", existing ref : " + str(arrear_ids)))

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
                    'code': "ARS",
                    'amount': arrear_data.arear_amount,
                    'contract_id': self.contract_id.id,
                    'ref': arrear_data.id,
                })

            self.input_line_ids = other_line_ids
