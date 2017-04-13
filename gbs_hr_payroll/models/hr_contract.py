from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class HrContract(models.Model):
    """
    Employee contract allows to add different values in fields.
    Fields are used in salary rule computation.
    """
    _inherit = 'hr.contract'

    transport_allowance = fields.Float(string='Trasport Allowance', digits=dp.get_precision('Payroll'),
                                    help='Amount for Transport Allowance')