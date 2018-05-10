from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProformaInvoice(models.Model):
    _name = 'proforma.invoice'
    _description = 'Proforma Invoice (PI)'
    _inherit = ['mail.thread']
    _rec_name='name'

    name = fields.Char(string='Name', index=True, readonly=True)
    #sale_order_id = fields.Many2one('sale.order',string='Sale Order Ref.', required=True,domain=[('state', '=', 'done')],readonly=True,states={'draft': [('readonly', False)]})

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
    sub_total = fields.Float(string='Sub Total', readonly=True)
    taxable_amount = fields.Float(string='Taxable Amount', readonly=True)
    untaxaed_amount = fields.Float(string='Untaxed Amount', readonly=True)
    taxed_amount = fields.Float(string='Tax', readonly=True)
    freight_charge = fields.Float(string='Freight Charge',readonly=True, states={'draft': [('readonly', False)]})
    total = fields.Float(string='Total', readonly=True)


    """ Relational field"""
    line_ids = fields.One2many('proforma.invoice.line', 'pi_no', string="Products", readonly=True, states={'draft': [('readonly', False)]})
    so_ids = fields.Many2many('sale.order', 'so_pi_rel', 'pi_no', 'so_id',
                              string='Sale Order',
                              readonly=True, states={'draft': [('readonly', False)]},
                              domain="[('pi_no', '=', False),('state', '=', 'done'), ('credit_sales_or_lc', '=','lc_sales')]")


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('proforma.invoice') or '/'
        vals['name'] = seq

        return super(ProformaInvoice, self).create(vals)



    @api.constrains('freight_charge', 'so_ids')
    def check_freight_charge_val(self):
        if self.freight_charge < 0:
            raise UserError('Freight Charge can not be Negative')

        # Below method is called here
        # to save onchanged readonly fields to DB
        self.so_product_line()


    @api.onchange('so_ids')
    def so_product_line(self):
        self.line_ids = []
        vals = []

        sub_total = 0
        taxed_amount = 0
        total = 0
        untaxaed_amount = 0

        for so_id in self.so_ids:

            sub_total += so_id.amount_untaxed
            taxed_amount += so_id.amount_tax
            total += so_id.amount_total
            untaxaed_amount += so_id.amount_untaxed

            for record in so_id.order_line:
                vals.append((0, 0, {'product_id': record.product_id.id,
                                   'quantity': record.product_uom_qty,
                                   'pack_type': so_id.pack_type.id,
                                   'uom_id': record.product_uom.id,
                                   'commission_rate': record.commission_rate,
                                   'price_unit': record.price_unit,
                                   'price_subtotal': record.price_subtotal,
                                   'tax': record.tax_id.id,
                                   }))



        self.sub_total = sub_total
        self.taxed_amount = taxed_amount
        self.total = total
        self.untaxaed_amount = untaxaed_amount

        self.line_ids = vals


    @api.multi
    def action_confirm(self):
        self.update_Pi_to_so_obj()
        self.state = 'confirmed'


    def update_Pi_to_so_obj(self):
        #Update PI to SO
        for so in self.so_ids:
            so.pi_no = self.id

            #update DA
            da_obj = so.env['delivery.authorization'].search([('sale_order_id', '=', so.id)])
            if da_obj:
                for da_ in da_obj:
                    da_.pi_no = self.id # update PI to DA if it is already created

            #update DO
            do_obj = so.env['delivery.order'].search([('sale_order_id', '=', so.id)])
            if do_obj:
                for do_ in do_obj:
                    do_.pi_no = self.id  # update PI to DO if it is already created



    @api.onchange('freight_charge')
    def onchange_freight_charge(self):
        if self.freight_charge < 0:
            raise UserError('Freight Charge can not be Negative')

        if self.freight_charge:
            self.total = self.total + self.freight_charge



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
    pi_no = fields.Many2one('proforma.invoice', ondelete='cascade')
