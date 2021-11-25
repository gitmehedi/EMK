from odoo import fields, models

class InheritHRPayslipsBatches(models.Model):
    _inherit = 'hr.payslip.run'

    # Salary With Bonus type removed
    type = fields.Selection([("0", "Regular Salary"),
                             ("1", "Festival Bonus")], "Type", required=True, default="0")


    festival_date = fields.Date('Festival Date')


class InheritHRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_default_type(self):
        if self.payslip_run_id:
            self.type = self.payslip_run_id
            data = self.type
            return data

        return "0"

    # Salary With Bonus type removed
    type = fields.Selection([("0", "Regular Salary"),
                             ("1", "Festival Bonus")], "Type",
                            required=True, default=_get_default_type)

    festival_date = fields.Date('Festival Date', related='payslip_run_id.festival_date', store=True)