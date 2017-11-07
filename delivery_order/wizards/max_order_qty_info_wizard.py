from odoo import models, fields


class MaxOrderQtyInfoWizard(models.TransientModel):
    _name ='max.order.wizard'
    _description = 'Max Order Info wizard'

    msg = fields.Text(string='', default = 'Hello Dolly!!', readonly=True)
