from odoo import api, fields, models, _


class ProformaInvoice(models.Model):
    _inherit = 'proforma.invoice'

    partner_id = fields.Many2one('res.partner', string='Customer',
                                 domain=[('customer', '=', True),
                                         ('parent_id', '=', False),
                                         ('is_deprecated', '=', False)])
    pack_type = fields.Many2one('product.packaging.mode', domain=[('is_deprecated', '=', False)])


class ProformaInvoiceLine(models.Model):
    _inherit = 'proforma.invoice.line'

    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True), ('is_deprecated', '=', False)])