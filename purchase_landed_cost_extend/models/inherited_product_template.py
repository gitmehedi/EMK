from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class InheritedProductTemplate(models.Model):
    _inherit = 'product.template'

    is_duty_tax = fields.Boolean(default=False, string="Is Duty/Tax",
                                  help="Take decision that, this service is a duty/tax.")

