from odoo import fields, models

class InheritHRPayslipsBatches(models.Model):
    _inherit = 'hr.payslip.run'

    type = fields.Selection([("0", "Regular Salary"),
                             ("1", "Festival Bonus"),
                             ("2", "Salary With Bonus")], "Type", required=True,default="0")
    festival_date = fields.Date('Festival Date')


class InheritHRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_default_type(self):
        active_id = self._context['active_id']
        if active_id:
            payslip_run_pool = self.env['hr.payslip.run']
            payslip_run = payslip_run_pool.search([('id','=',active_id)])
            if payslip_run:
                return payslip_run.type

        return "0"

    type = fields.Selection([("0", "Regular Salary"),
                             ("1", "Festival Bonus"),
                             ("2", "Salary With Bonus")], "Type",
                            required=True, default=_get_default_type)

    festival_date = fields.Date('Festival Date',related='payslip_run_id.festival_date',store=True)
