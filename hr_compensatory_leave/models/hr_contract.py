from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class HrContract(models.Model):
    _inherit = 'hr.contract'

    comp_allow_rate = fields.Float(string='Compensatory Allowance Rate', digits=dp.get_precision('Payroll'),
                                   track_visibility='onchange')
