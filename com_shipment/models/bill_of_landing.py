from odoo import api, fields, models

class BillOfLanding(models.Model):
    _name = 'bill.of.landing'
    _description = 'Bill Of Landing'
    _order = "id desc"

    name = fields.Char(string='Number', required=True, index=True)
    shipment_date = fields.Date('Ship on Board', required=True)
    file = fields.Binary(default='Bill Of Landing Copy')