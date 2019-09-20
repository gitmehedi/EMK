from odoo import models, fields, api
from odoo.exceptions import UserError


class HrEmployeeIouWizard(models.TransientModel):
    _name = 'hr.employee.iou.wizard'

    repay = fields.Float(string="RePay", required=True)

    @api.multi
    def process_repayment(self):

        emp_iou_pool = self.env['hr.employee.iou'].browse([self._context['active_id']])

        amount = emp_iou_pool.amount
        due_amount = emp_iou_pool.due
        emp_id = emp_iou_pool.employee_id.id

        if self.repay is not None and amount is not None:
            if(self.repay > amount or self.repay > due_amount):
                raise UserError(('Repayment can not be greater than actual amount'))

        if self.repay:
            self.env['hr.employee.iou.line'].create({
                'iou_id':self._context['active_id'],
                'repay_amount': self.repay, 'employee_id': emp_id
            })

