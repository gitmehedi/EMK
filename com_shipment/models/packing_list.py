from odoo import api, fields, models

class PackingList(models.Model):

    _name = 'packing.list'
    _description = 'Packing List'
    _order = "id desc"

    gross_weight = fields.Float('Gross Weight', required=True)
    net_weight = fields.Float('Net Weight', required=True)
    file = fields.Binary(default='Packing List Copy')