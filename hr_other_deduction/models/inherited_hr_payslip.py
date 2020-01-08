from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class InheritHRPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    ref = fields.Char('Reference')


class InheritHRPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def action_payslip_done(self):
        res = super(InheritHRPayslip, self).action_payslip_done()

        od_ids = []
        pay_slip_input = []
        for input in self.input_line_ids:
            if input.code == 'ODS':
                od_ids.append(int(input.ref))
                pay_slip_input.append(input.id)

        od_line_pool = self.env['hr.other.deduction.line']
        od_data = od_line_pool.browse(od_ids)
        if od_data.exists():
            od_data.write({'state': 'adjusted'})
        elif len(od_ids) > 0:
            raise ValidationError(_("Other deduction Data Error For: " + self.name + " hr_payslip_id :" + str(self.id) + ". Need to Update 'ref' from hr_pay_slip_input where id is :" + str(pay_slip_input)+", existing ref : " + str(od_ids)))

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
