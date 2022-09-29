from odoo import fields, models, api


class InheritedStockMove(models.Model):
    _inherit = 'stock.move'

    challan_bill_no = fields.Char(string='Challan Bill No')

    challan_date = fields.Date(string='Challan Date')

