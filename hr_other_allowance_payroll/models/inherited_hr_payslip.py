from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class InheritHRPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    ref = fields.Char('Reference')

    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHRPayslipInput, self).action_payslip_done()

        other_ids = []
        pay_slip_input = []
        for input in self.input_line_ids:
            if input.code == 'OAS':
                other_ids.append(int(input.ref))
                pay_slip_input.append(input.id)

        other_line_pool = self.env['hr.other.allowance.line']
        other_data = other_line_pool.browse(other_ids)
        if other_data.exists():
            other_data.write({'state': 'adjusted'})
        elif len(other_ids) > 0:
            raise ValidationError(_("Other allowance Data Error For: " + self.name + " hr_payslip_id :" + str(self.id) + ". Need to Update 'ref' from hr_pay_slip_input where id is :" + str(pay_slip_input)+", existing ref : " + str(other_ids)))

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
            other_datas = self.env['hr.other.allowance.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('state','=','approved')])

            """
            Other Allowance Bills
            """
            for other_data in other_datas:
                other_line_ids += other_line_ids.new({
                    'name': 'Other Allowance',
                    'code': "OAS",
                    'amount': other_data.other_allowance_amount,
                    'contract_id': self.contract_id.id,
                    'ref': other_data.id,
                })

            self.input_line_ids = other_line_ids
