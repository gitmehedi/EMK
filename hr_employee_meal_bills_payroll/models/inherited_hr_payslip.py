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

        meal_ids = []
        pay_slip_input = []
        for input in self.input_line_ids:
            if input.code == 'MEAL':
                meal_ids.append(int(input.ref))
                pay_slip_input.append(input.id)

        meal_line_pool = self.env['hr.meal.bill.line']
        meal_data = meal_line_pool.browse(meal_ids)
        if meal_data.exists():
            meal_data.write({'state':'adjusted'})
        elif len(meal_ids) > 0:
            raise ValidationError(_("Meal Bill Data Error For: "+ self.name + " hr_payslip_id :"+ str(self.id) + ". Need to Update 'ref' from hr_pay_slip_input where id is :"+ str(pay_slip_input)+", existing ref : "+ str(meal_ids)))

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = 0
            super(InheritHRPayslip, self).onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            meal_datas = self.env['hr.meal.bill.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('state','=','approved')])

            """
            Meal Bills
            """
            for meal_data in meal_datas:
                other_line_ids += other_line_ids.new({
                    'name': 'Meal Bill',
                    'code': "MEAL",
                    'amount': meal_data.bill_amount,
                    'contract_id': self.contract_id.id,
                    'ref': meal_data.id,
                })

            self.input_line_ids = other_line_ids
