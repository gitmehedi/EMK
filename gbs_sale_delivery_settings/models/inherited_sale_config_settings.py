from odoo import api, fields, models

class SaleConfigSettings(models.TransientModel):
    _inherit = "sale.config.settings"

    delivery_order_auto_generate = fields.Selection([
        (1, "Generate Delivery Order Automatically"),
        (0, 'Do Not Generate Delivery Order Automatically'),
    ], "Delivery Order Generating")
