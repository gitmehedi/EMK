from odoo import api, fields, models


class InheritedHrMobilePayslip(models.Model):
    _inherit = "hr.payslip"

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedHrMobilePayslip, self).onchange_employee()

            other_line_ids = self.input_line_ids
            emp_iou_pool = self.env['hr.employee.iou'].search([('employee_id', '=', self.employee_id.id)], limit=1)

            if emp_iou_pool and self.contract_id.id and emp_iou_pool.state=='confirm':
                other_line_ids += other_line_ids.new({
                        'name': 'Employee IOU',
                        'code': "IOU",
                        'amount': emp_iou_pool.due,
                        'contract_id': self.contract_id.id,
                })

            self.input_line_ids = other_line_ids
