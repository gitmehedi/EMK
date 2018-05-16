from odoo import fields, models

class InheritHRPayslipsBatches(models.Model):
    _inherit = 'hr.payslip.run'

    type = fields.Selection([("salary", "Regular Salary"),
                             ("salary", "Bonus"),
                             ("sl_bonus", "Salary With Bonus")], "Type", required=True)


class InheritHRPayslip(models.Model):
    _inherit = 'hr.payslip'

    type = fields.Selection(related='payslip_run_id.type',store=True)
