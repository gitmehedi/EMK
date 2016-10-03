from openerp import models, fields

class delivery_courier(models.Model):
    
    _name = "delivery.courier"
    
    name = fields.Char(
        string='Name',
        size=128,
        required=True,
        )
    active = fields.Boolean(
        string="Active")