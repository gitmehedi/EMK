from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProformaInvoice(models.Model):
    _name = 'proforma.invoice'
    _description = 'Proforma Invoice (PI)'
    _inherit = ['mail.thread']
    _rec_name='name'

    name = fields.Char(string='Name', index=True, readonly=True)
    sale_order_id = fields.Many2one('sale.order',string='Sale Order Ref.', required=True,domain=[('state', '=', 'done')],readonly=True,states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)],required=True,readonly=True,states={'draft': [('readonly', False)]})
    invoice_date = fields.Date('Invoice Date', readonly=True,states={'draft': [('readonly', False)]})
    advising_bank = fields.Text(string='Advising Bank', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,required=True, states={'draft': [('readonly', False)]})
    country_of_origin = fields.Char(string='Country of Origin',readonly=True, states={'draft': [('readonly', False)]})

    """ Shipping Address"""
    ship_freight_type = fields.Char(string='Freight Type',readonly=True,states={'draft': [('readonly', False)]})
    ship_exp_date = fields.Char(string='Exp. Shipping Date',readonly=True,states={'draft': [('readonly', False)]})
    ship_exp_good_weight = fields.Char(string='Exp. Goods Weight',readonly=True,states={'draft': [('readonly', False)]})
    ship_exp_cubic_weight = fields.Char(string='Exp. Cubic Weight',readonly=True,states={'draft': [('readonly', False)]})
    ship_total_pkg = fields.Char(string='Total Package',readonly=True,states={'draft': [('readonly', False)]})

    """ Customer Address"""
    customer_add = fields.Text(string='Customer Address',readonly=True,states={'draft': [('readonly', False)]})

    """ Ship To"""
    ship_to_add = fields.Text(string='Ship To Address',readonly=True,states={'draft': [('readonly', False)]})
    terms_condition = fields.Text(string='Terms of Condition', readonly=True, states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed")
    ], default='draft')

    sequence_id = fields.Char('Sequence', readonly=True)

    """ Calculations fields after """
    sub_total = fields.Float(string='Sub Total',readonly=True)
    taxable_amount = fields.Float(string='Taxable Amount',readonly=True)
    taxed_amount = fields.Float(string='Tax',readonly=True)
    freight_charge = fields.Float(string='Freight Charge',readonly=True, states={'draft': [('readonly', False)]})
    total = fields.Float(string='Total', readonly=True)


    """ Relational field"""
    line_ids = fields.One2many('proforma.invoice.line', 'parent_id', string="Products", readonly=True, states={'draft': [('readonly', False)]})


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('proforma.invoice') or '/'
        vals['name'] = seq
        return super(ProformaInvoice, self).create(vals)

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'


    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        self.set_products_info_automatically()

    @api.constrains('freight_charge','sale_order_id')
    def check_freight_charge_val(self):
        if self.freight_charge < 0:
            raise UserError('Freight Charge can not be minus value')

        sale_order_obj = self.env['sale.order'].search([('id', '=', self.sale_order_id.id)])

        if sale_order_obj:
            self.sub_total = sale_order_obj.amount_untaxed
            self.taxed_amount = sale_order_obj.amount_tax
            self.total = sale_order_obj.amount_total

        if self.freight_charge:
            self.total = sale_order_obj.amount_total + self.freight_charge

    @api.onchange('freight_charge')
    def onchange_freight_charge(self):
        if self.freight_charge < 0:
            raise UserError('Freight Charge can not be minus value')

        sale_order_obj = self.env['sale.order'].search([('id', '=', self.sale_order_id.id)])

        if self.freight_charge:
            self.total = sale_order_obj.amount_total + self.freight_charge


    def set_products_info_automatically(self):
        if self.sale_order_id:
            val = []
            sale_order_obj = self.env['sale.order'].search([('id', '=', self.sale_order_id.id)])

            if sale_order_obj:
                self.partner_id = sale_order_obj.partner_id.id
                self.sub_total = sale_order_obj.amount_untaxed
                self.taxed_amount = sale_order_obj.amount_tax
                self.total = sale_order_obj.amount_total
                self.currency_id = sale_order_obj.currency_id.id

                for record in sale_order_obj.order_line:
                    val.append((0, 0, {'product_id': record.product_id.id,
                                       'quantity': record.product_uom_qty,
                                       'pack_type': sale_order_obj.pack_type.id,
                                       'uom_id': record.product_uom.id,
                                       'commission_rate': record.commission_rate,
                                       'price_unit': record.price_unit,
                                       'price_subtotal': record.price_subtotal,
                                       'tax':record.tax_id.id,
                                       }))

            self.line_ids = val


class ProformaInvoiceLine(models.Model):
    _name = 'proforma.invoice.line'
    _description = 'Proforma Invoice Line (PI Line)'

    """ Line values"""
    product_id = fields.Many2one('product.product', string="Product", ondelete='cascade',readonly=True)
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='cascade',readonly=True)
    quantity = fields.Float(string="Ordered Qty", default="1",readonly=True)
    price_unit = fields.Float(string="Price Unit",readonly=True)
    tax = fields.Many2one('account.tax',string='Tax (%)',readonly=True)
    price_subtotal = fields.Float(string="Price Subtotal", readonly=True)

    """ Relational field"""
    parent_id = fields.Many2one('proforma.invoice', ondelete='cascade')
