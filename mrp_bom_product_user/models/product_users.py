from odoo import fields, models, api,_
from odoo.exceptions import ValidationError


class InheritUsers(models.Model):
    _inherit = "res.users"

    product_ids = fields.Many2many('product.template', 'product_users_rel', 'user_id', 'product_id', 'Allow Products',
                                   domain=[('manufacture_ok', '=', True)])
