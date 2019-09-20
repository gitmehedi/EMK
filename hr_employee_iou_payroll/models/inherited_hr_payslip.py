from odoo import api, fields, models


class InheritedEmployeeIouPayslip(models.Model):
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.multi
    def action_payslip_done(self):
        res = super(InheritedEmployeeIouPayslip, self).action_payslip_done()

        iou_ids = []
        for input in self.input_line_ids:
            if input.code == 'IOU':
                iou_ids.append(int(input.ref))

        iou_pool = self.env['hr.employee.iou']
        iou_line_pool = self.env['hr.employee.iou.line']
        for iou in iou_pool.browse(iou_ids):
            vals = {}
            vals['employee_id'] = iou.employee_id.id
            vals['repay_amount'] = iou.due
            vals['iou_id'] = iou.id
            iou_line_pool.create(vals)

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedEmployeeIouPayslip, self).onchange_employee()

            other_line_ids = self.input_line_ids
            emp_iou_pool = self.env['hr.employee.iou'].search([('employee_id', '=', self.employee_id.id),
                                                               ('state','=','confirm')])

            for iou_data in emp_iou_pool:
                if iou_data.due > 0.0:
                    other_line_ids += other_line_ids.new({
                            'name': 'Employee IOU',
                            'code': "IOU",
                            'amount': iou_data.due,
                            'contract_id': self.contract_id.id,
                            'ref': iou_data.id,
                    })

            self.input_line_ids = other_line_ids
