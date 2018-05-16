from odoo import fields, models

class InheritHRPayslipsBatches(models.Model):
    _inherit = 'hr.payslip.run'

    type = fields.Selection([("0", "Regular Salary"),
                             ("1", "Festival Bonus"),
                             ("2", "Salary With Bonus")], "Type", required=True)


class InheritHRPayslip(models.Model):
    _inherit = 'hr.payslip'

    type = fields.Selection(related='payslip_run_id.type',store=True)
