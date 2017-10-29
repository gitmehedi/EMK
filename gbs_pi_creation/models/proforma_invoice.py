from odoo import api, fields, models

class ProformaInvoice(models.Model):
    _name = 'proforma.invoice'
    _description = 'Proforma Invoice (PI)'
    _inherit = ['mail.thread']
    _rec_name='name'

    name = fields.Char(string='Name', index=True, readonly=True)
    partner_id = fields.Many2one('res.partner',string='Customer', required=True)
    invoice_date = fields.Date('Invoice Date', readonly=True,required=True, states={'confirm': [('readonly', False)]})
    advising_bank = fields.Char(string='Advising Bank', states={'confirm': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,required=True, states={'confirm': [('readonly', False)]})
    country_of_origin = fields.Char(string='Country of Origin',readonly=True, states={'confirm': [('readonly', False)]})

    """ Shipping Address"""
    ship_freight_type = fields.Char(string='Freight Type')
    ship_exp_date = fields.Char(string='Exp. Shipping Date')
    ship_exp_good_weight = fields.Char(string='Exp. Goods Weight')
    ship_exp_cubic_weight = fields.Char(string='Exp. Cubic Weight')
    ship_total_pkg = fields.Char(string='Total Package')

    """ Customer Address"""
    customer_add = fields.Text(string='Customer Addrss')

    """ Ship To"""
    ship_to_add = fields.Text(string='Ship To Address')
    terms_condition = fields.Text(string='Terms of Condition', readonly=True, states={'confirm': [('readonly', False)]})

    state = fields.Selection([
        ('confirm', "Confirm"),
        ('approve', "Approved")
    ], default='confirm')

    sequence_id = fields.Char('Sequence', readonly=True)

    """ Relational field"""
    line_ids = fields.One2many('proforma.invoice.line', 'parent_id', string="Products", readonly=True, states={'confirm': [('readonly', False)]})


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('proforma.invoice') or '/'
        vals['name'] = seq
        return super(ProformaInvoice, self).create(vals)

    @api.multi
    def action_confirm(self):
        self.state = 'approve'

class ProformaInvoiceLine(models.Model):
    _name = 'proforma.invoice.line'
    _description = 'Proforma Invoice Line (PI Line)'

    """ Line values"""
    product_id = fields.Many2one('product.product', string="Product", ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='cascade')
    quantity = fields.Float(string="Ordered Qty", default="1")
    price_unit = fields.Float(string="Price Unit")
    tax = fields.Many2one('account.tax',string='Tax (%)')
    price_subtotal = fields.Float(string="Price Subtotal", readonly=True)

    """ Calculations fields after """
    sub_total = fields.Float(string='Sub Total',readonly=True)
    taxable_amount = fields.Float(string='Taxable Amount',readonly=True)
    taxed_amount = fields.Float(string='Taxed Amount',readonly=True)
    freight_charge = fields.Float(string='Freight Charge',readonly=True)
    total = fields.Float(string='Total', readonly=True)

    """ Relational field"""
    parent_id = fields.Many2one('proforma.invoice', ondelete='cascade')
