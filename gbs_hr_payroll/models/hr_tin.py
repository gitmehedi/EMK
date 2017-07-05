from odoo import api, fields, models, _

class HrContract(models.Model):

    _inherit = 'hr.employee'

    mob_bill_unlimited = fields.Float(string='Trasport Allowance')