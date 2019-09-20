from odoo import api, fields, models,_


class LCProduct(models.Model):
    _name = 'lc.product.line'
    _description = 'Lc Product Line'
    _order = "date_planned desc"

    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)

    product_qty = fields.Float(string='LC Quantity')
    product_received_qty = fields.Float(string='Received Quantity')
    price_unit = fields.Float(string='Unit Price')
    currency_id = fields.Many2one('res.currency', 'Currency')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')

    lc_id = fields.Many2one('letter.credit', string='LC')
    # Check test for foreign sales

    # Another test for foreign sales
    # commit from samuda-live-qa
