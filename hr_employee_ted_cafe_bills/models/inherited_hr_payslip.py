from odoo import api, fields, models, tools, _


class InheritedHrTedCafePayslip(models.Model):
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.multi
    def action_payslip_done(self):
        res = super(InheritedHrTedCafePayslip, self).action_payslip_done()

        tcb_ids = []
        for line in self.input_line_ids:
            if input.code == 'TCB':
                tcb_ids.append(int(line.ref))

        tcb_data = self.env['hr.ted.cafe.bill.line'].browse(tcb_ids)
        tcb_data.write({'state': 'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedHrTedCafePayslip, self).onchange_employee()

            line_ids = self.input_line_ids
            lines = self.env['hr.ted.cafe.bill.line'].search([('employee_id', '=', self.employee_id.id),
                                                            ('state', '=', 'applied')])

            for line in lines:
                line_ids += line_ids.new({
                    'name': 'Ted Cafe Bill',
                    'code': "TCB",
                    'amount': line.amount,
                    'contract_id': self.contract_id.id,
                    'ref': line.id,
                })
            self.input_line_ids = line_ids
