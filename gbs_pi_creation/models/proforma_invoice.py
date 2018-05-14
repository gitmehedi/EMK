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
    sub_total = fields.Float(string='Sub Total', readonly=True, store=True)
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
                              domain="[('pi_no', '=', False), ('state', '=', 'done'), ('credit_sales_or_lc', '=','lc_sales')]")


    def _prepare_lines_by_so_ids(self, so_ids):
        res = []
        product_list = []
        for so in so_ids:
            for line in so.order_line:
                new_prod = True
                for prod in product_list:
                    if line.product_id.id == prod['product_id']:
                        new_prod = False
                        ### Need Update
                        total_qty = line.product_uom_qty + prod['quantity']
                        total_price_subtotal = line.price_subtotal + prod['price_subtotal']
                        avg_unit_price = total_price_subtotal / (total_qty * 1.0)  # to ensure flaot value multily with 1.0

                        prod.update({
                            'quantity': total_qty,
                            'price_unit': avg_unit_price,
                            'price_subtotal': total_price_subtotal
                        })

                if new_prod:
                    prod_line = {'product_id': line.product_id.id,
                                 'quantity': line.product_uom_qty,
                                 'pack_type': so.pack_type.id,
                                 'uom_id': line.product_uom.id,
                                 'commission_rate': line.commission_rate,
                                 'price_unit': line.price_unit,
                                 'price_subtotal': line.price_subtotal,
                                 'tax': line.tax_id.id,
                                 }
                    product_list.append(prod_line)


        for prod in product_list:
            res.append([0, 0, prod])

        return res

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('proforma.invoice') or '/'
        vals['name'] = seq

        if vals.get('so_ids'):
            so_ids = self.env['sale.order'].search([('id', 'in', vals.get('so_ids')[0][2])])
            result = self._prepare_lines_by_so_ids(so_ids)
            self.update_total_info(vals)

            vals['line_ids'] = result

        return super(ProformaInvoice, self).create(vals)


    @api.multi
    def write(self, vals, context=None):
        if self.state == 'draft' and vals.get('so_ids'):
            self.update_total_info(vals)

        if self.state == 'confirmed':
             vals['so_ids'] = vals['so_ids'].ids
        return super(ProformaInvoice, self).write(vals)


    def update_total_info(self, vals):
        sub_total = 0
        taxed_amount = 0
        total = 0
        untaxed_amount = 0

        so_ids = self.env['sale.order'].search([('id', 'in', vals['so_ids'][0][2])])

        for so in so_ids:
            sub_total += so.amount_untaxed
            taxed_amount += so.amount_tax
            total += so.amount_total
            untaxed_amount += so.amount_untaxed

        vals['sub_total'] = sub_total
        vals['taxed_amount'] = taxed_amount
        vals['total'] = total
        vals['untaxed_amount'] = untaxed_amount


    @api.constrains('freight_charge')
    def check_freight_charge_val(self):
        if self.freight_charge < 0:
            raise UserError('Freight Charge can not be Negative')


    @api.onchange('so_ids')
    def so_product_line(self):

        sub_total = 0
        taxed_amount = 0
        total = 0
        untaxed_amount = 0

        for so in self.so_ids:
            if self.partner_id and self.partner_id != so.partner_id:
                raise ValidationError('Please add Sale Order whose Customer is same.')
            else:
                self.partner_id = so.partner_id
                self.currency_id = so.currency_id


            sub_total += so.amount_untaxed
            taxed_amount += so.amount_tax
            total += so.amount_total
            untaxed_amount += so.amount_untaxed

        self.line_ids = self._prepare_lines_by_so_ids(self.so_ids)

        self.sub_total = sub_total
        self.taxed_amount = taxed_amount
        self.total = total
        self.untaxed_amount = untaxed_amount



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
    product_id = fields.Many2one('product.product', string="Product", ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='cascade', readonly=True)
    quantity = fields.Float(string="Ordered Qty")
    price_unit = fields.Float(string="Price Unit", readonly=True)
    tax = fields.Many2one('account.tax', string='Tax (%)')
    price_subtotal = fields.Float(string="Price Subtotal", readonly=True)

    """ Relational field"""
    pi_no = fields.Many2one('proforma.invoice', ondelete='cascade')



    @api.onchange('product_id')
    def onchange_product_id(self):
        # Fetch Active price for this product
        active_prod_price_pool = self.env['product.sale.history.line'].search([('product_id','=',self.product_id.id)])

        print active_prod_price_pool.currency_id.id

        self.uom_id = active_prod_price_pool.uom_id
        self.price_unit = active_prod_price_pool.new_price
        self.quantity = 1
        self.price_subtotal = self.price_unit * self.quantity

        ## Set Proforma Invoice Table value
        #self.pi_no.currency_id.id = active_prod_price_pool.currency_id.id
        self.pi_no.sub_total = self.price_subtotal
        self.pi_no.taxed_amount = self.calculate_tax_amount(self.tax.id, self.price_subtotal)
        self.pi_no.untaxaed_amount = self.price_subtotal
        self.pi_no.total = self.pi_no.taxed_amount + self.price_subtotal



    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.quantity < 0:
            raise UserError('Quantity can not be Negative')

        self.price_subtotal = self.price_unit * self.quantity

        ## Set Proforma Invoice Table value
        # self.pi_no.currency_id.id = active_prod_price_pool.currency_id.id
        self.pi_no.sub_total = self.price_subtotal
        self.pi_no.taxed_amount = self.calculate_tax_amount(self.tax.id, self.price_subtotal)
        self.pi_no.untaxed_amount = self.price_subtotal
        self.pi_no.total = self.pi_no.taxed_amount + self.price_subtotal


    def calculate_tax_amount(self, tax_id, total_price):
        if tax_id:
            tax_pool = self.env['account.tax'].search([('id','=',tax_id)])
            return (tax_pool.amount/100) * total_price



