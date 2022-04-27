from odoo import fields, models, api

class InheritedPaySlipsBatch(models.Model):
    _inherit = 'hr.payslip.run'

    type = fields.Selection(selection_add=[('2', 'OT')])


class InheritHRPayslip(models.Model):
    _inherit = 'hr.payslip'

    type = fields.Selection(selection_add=[('2', 'OT')])