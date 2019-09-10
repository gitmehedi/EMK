from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class ProformaInvoice(models.Model):
    _name = 'proforma.invoice'
    _description = 'Proforma Invoice (PI)'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id DESC'
    _rec_name = 'name'

    @api.depends('line_ids.price_unit','line_ids.tax', 'line_ids.price_subtotal', 'line_ids.quantity' ,'freight_charge','currency_id')
    def _amount_all(self):
        for pi in self:
            amount_subtotal = amount_untaxed = amount_tax = 0.0
            for line in pi.line_ids:
                amount_subtotal += line.price_subtotal
                amount_untaxed += line.price_unit * line.quantity
                # FORWARDPORT UP TO 10.0
                if pi.beneficiary_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.tax.compute_all(line.price_unit, pi.currency_id, line.quantity,
                                                 product=line.product_id, partner=pi.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax

                pi.sub_total = amount_subtotal
                pi.untaxaed_amount= amount_untaxed
                pi.taxed_amount= amount_tax
                pi.total= amount_untaxed + amount_tax + pi.freight_charge

    @api.depends('partner_id')
    def _compute_customer_address(self, context=None):
        if self.partner_id:
            str_address = self.getAddressByPartner(self.partner_id)
            self.customer_add = str_address

    name = fields.Char(string='Name', index=True, readonly=True, default="/")
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True),('parent_id', '=', False)], required=True,
                                 track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]})
    invoice_date = fields.Date('PI Date', readonly=True, required=True,track_visibility='onchange',
                               states={'draft': [('readonly', False)]},default=fields.Datetime.now)
    # advising_bank_id = fields.Many2one('res.bank', string='Advising Bank', readonly=True,
    #                                    states={'draft': [('readonly', False)]})

    advising_bank_acc_id = fields.Many2one('res.partner.bank', string='Advising Bank Acc', track_visibility='onchange', domain=[('is_company_account', '=', True)],
                                           required=True, readonly=True, states={'draft': [('readonly', False)]})

    region_type = fields.Selection([('local', "Local"),('foreign', "Foreign")], readonly=True,)


    beneficiary_id = fields.Many2one('res.company', string='Beneficiary', required=True, readonly=True,track_visibility='onchange',
                                     default=lambda self: self.env['res.company']._company_default_get(),
                                     states={'draft': [('readonly', False)]})

    transport_by = fields.Char(string='Transport By', required=True, readonly=True,track_visibility='onchange',
                               states={'draft': [('readonly', False)]},default='By Truck')
    terms_condition = fields.Text(string='Terms & Conditions', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})

    # terms_id = fields.Many2one('terms.setup', string='Old Payment term', store=True, readonly=True,
    #                            track_visibility='onchange',
    #                            states={'draft': [('readonly', False)]})

    account_payment_term_id = fields.Many2one('account.payment.term', string='Payment term', store=True, readonly=True,
                                              track_visibility='onchange', states={'draft': [('readonly', False)]})

    terms_of_delivery = fields.Char(string='Terms of Delivery', readonly=True, track_visibility='onchange',
                               states={'draft': [('readonly', False)]}, default='')

    """ Shipping Address"""
    ship_freight_type = fields.Char(string='Freight Type', readonly=True, states={'draft': [('readonly', False)]})
    ship_exp_date = fields.Date(string='Exp. Shipping Date', readonly=True, states={'draft': [('readonly', False)]})
    ship_exp_good_weight = fields.Char(string='Exp. Goods Weight', readonly=True,
                                       states={'draft': [('readonly', False)]})
    ship_exp_cubic_weight = fields.Char(string='Exp. Cubic Weight', readonly=True,
                                        states={'draft': [('readonly', False)]})
    ship_total_pkg = fields.Char(string='Total Package', readonly=True, states={'draft': [('readonly', False)]})

    """ Customer Address"""
    customer_add = fields.Text(string='Customer Address',store=True, readonly=True,track_visibility='onchange',
                               compute='_compute_customer_address')

    """ Ship To"""
    terms_condition = fields.Text(string='Terms of Condition', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    packing = fields.Char(string='Packing', readonly=True, track_visibility='onchange',
                          states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed")
    ], default='draft', track_visibility='onchange')

    sequence_id = fields.Char('Sequence', readonly=True)

    """ Calculations fields after """
    sub_total = fields.Float(string='Sub Total', readonly=True,compute='_amount_all',store = True)
    taxable_amount = fields.Float(string='Taxable Amount')
    untaxaed_amount = fields.Float(string='Untaxed Amount', readonly=True ,compute='_amount_all',store = True)
    taxed_amount = fields.Float(string='Tax', readonly=True,compute='_amount_all',store = True)
    freight_charge = fields.Float(string='Freight Charge', readonly=True, states={'draft': [('readonly', False)]},
                                  track_visibility='onchange')
    total = fields.Float(string='Total', readonly=True, track_visibility='onchange',compute='_amount_all',store = True)

    """ Relational field"""
    line_ids = fields.One2many('proforma.invoice.line', 'pi_id', string="Products", track_visibility='onchange',readonly=True,
                               states={'draft': [('readonly', False)]})

    def _get_pack_type(self):
        return self.env['product.packaging.mode'].search([], limit=1)

    """New field"""
    pack_type = fields.Many2one('product.packaging.mode', string='Packing Mode', default=_get_pack_type,
                                readonly=True, track_visibility='onchange',
                                states={'draft': [('readonly', False)]}
                                , required=True)
    type_id = fields.Many2one(comodel_name='sale.order.type', string='Type', domain=[('sale_order_type', 'in', ['lc_sales', 'tt_sales', 'contract_sales'])], readonly=True,
                              required=True,track_visibility='onchange',states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(comodel_name='res.currency',related='type_id.currency_id', store=True,
                                  string='Currency',readonly=True,track_visibility='onchange')
    credit_sales_or_lc = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
        ('tt_sales', 'TT'),
        ('contract_sales', 'Sales Contract'),
    ], string='Sales Type', readonly=True,related='type_id.sale_order_type')

    @api.multi
    @api.onchange('currency_id')
    def currency_id_onchange(self):
        for order in self:
            for line in order.line_ids:
                line._set_product_line()

    @api.multi
    @api.onchange('pack_type')
    def pack_type_onchange(self):
        for order in self:
            for line in order.line_ids:
                line._set_product_line()



    @api.constrains('freight_charge')
    def check_freight_charge_val(self):
        if self.freight_charge < 0:
            raise UserError('Freight Charge can not be Negative')

    def getAddressByPartner(self, partner):

        address = partner.address_get(['delivery', 'invoice'])
        delivery_address = self.env['res.partner'].browse(address['delivery'])

        address = []
        if delivery_address.street:
            address.append(delivery_address.street)

        if delivery_address.street2:
            address.append(delivery_address.street2)

        if delivery_address.zip_id:
            address.append(delivery_address.zip_id.name)

        if delivery_address.city:
            address.append(delivery_address.city)

        if delivery_address.state_id:
            address.append(delivery_address.state_id.name)

        if delivery_address.country_id:
            address.append(delivery_address.country_id.name)

        str_address = '\n '.join(address)

        return str_address

    @api.multi
    def action_confirm(self):
        res = {'state': 'confirm'}
        if self.name == "/":
            new_seq = self.env['ir.sequence'].next_by_code_new('proforma.invoice', self.invoice_date, self.operating_unit_id)
            if new_seq:
                res['name'] = new_seq
        self.write(res)

    @api.multi
    def action_draft(self):
        so_obj = self.env['sale.order'].search([('pi_id','=',self.id)])
        if not so_obj:
            res = {
                'state': 'draft',
            }
            self.write(res)
        else:
            raise ValidationError("You can't reset this PI!! \n PI is associate with sale order (" +so_obj.name+ ") reference.")

    @api.onchange('account_payment_term_id')
    def _account_payment_term_id(self):
        if self.account_payment_term_id:
            self.terms_condition = self.account_payment_term_id.terms_condition

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft'])]

        ## mail notification
        # @api.multi
        # def _notify_approvers(self):
        #     approvers = self.employee_id._get_employee_manager()
        #     if not approvers:
        #         return True
        #     for approver in approvers:
        #         self.sudo(SUPERUSER_ID).add_follower(approver.id)
        #         if approver.sudo(SUPERUSER_ID).user_id:
        #             self.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
        #                 [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        #     return True

    #########################################
    # PI Operating Unit related code - STARTS
    #########################################
    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        required=True,track_visibility='onchange')

    @api.model
    def _default_sales_team(self):
        team = self.env['crm.team']._get_default_team_id()
        if team:
            return team.id

    sales_team_id = fields.Many2one('crm.team', string='Sales Team', readonly=True,
                                    default=_default_sales_team, track_visibility='onchange')


    ########################################
    # PI Operating Unit related code - ENDS
    ########################################

    @api.constrains('line_ids')
    def _check_multiple_products_line(self):
        if len(self.line_ids) > 1:
            raise ValidationError("You can't add multiple products")



# ---------------------------------------------------------------------------------------------------------------------------------
class ProformaInvoiceLine(models.Model):
    _name = 'proforma.invoice.line'
    _description = 'Proforma Invoice Line (PI Line)'

    """ Line values"""
    product_id = fields.Many2one('product.product', string="Product", required=True)
    description = fields.Char(related='product_id.name', store=True,string='Description',
                              readonly=True)
    uom_id = fields.Many2one('product.uom', string="Unit of Measure", store=True,related='product_id.uom_id',
                             readonly=True)
    quantity = fields.Float(string="Ordered Qty",default=1)
    price_unit = fields.Float(string="Unit Price", digits=dp.get_precision('Product Price'))
    tax = fields.Many2one('account.tax', string='Taxes')
    price_tax = fields.Float(compute='_compute_amount', store=True, string='Tax')
    price_subtotal = fields.Float(string="Sub Total", store=True,compute='_get_price_subtotal',readonly=True)

    """ Relational field"""
    pi_id = fields.Many2one('proforma.invoice', ondelete='cascade')

    @api.constrains('quantity')
    def check_quantity(self):
        if self.quantity < 0:
            raise UserError('Quantity can not be Negative')


    @api.depends('quantity','price_unit','price_tax')
    def _get_price_subtotal(self):
        for line in self:
            if line.price_tax:
                line.price_subtotal = line.price_unit * line.quantity + line.price_tax
            else:
                line.price_subtotal = line.price_unit * line.quantity


    @api.depends('quantity', 'price_unit', 'tax')
    def _compute_amount(self):
        for line in self:
            taxes = line.tax.compute_all(line.price_unit, line.pi_id.currency_id, line.quantity, product=line.product_id, partner=line.pi_id.partner_id)
            line.price_tax= taxes['total_included'] - taxes['total_excluded']

    @api.onchange('product_id')
    def onchange_product_id(self):
        self._set_product_line()

    def _set_product_line(self):
        if self.product_id:
            self.price_unit = self._get_product_sales_price(self.product_id)

    # @api.depends('product_id','pi_id.currency_id')
    def _get_product_sales_price(self,product):
        if product:
            if not self.uom_id:
                self.uom_id = self.product_id.uom_id

            price_change_pool = self.env['product.sale.history.line'].search(
                [('product_id', '=', product.id),
                 ('currency_id', '=', self.pi_id.currency_id.id),
                 ('product_package_mode', '=', self.pi_id.pack_type.id),
                 ('uom_id', '=', self.uom_id.id)])

            if not price_change_pool:
                price_change_pool = self.env['product.sale.history.line'].search(
                    [('product_id', '=', product.id),
                     ('currency_id', '=', self.pi_id.currency_id.id),
                     ('product_package_mode', '=', self.pi_id.pack_type.id),
                     ('category_id', '=', self.uom_id.category_id.id)])

                if price_change_pool:
                    if not price_change_pool.uom_id.uom_type == "reference":
                        uom_base_price = price_change_pool.new_price / price_change_pool.uom_id.factor_inv
                    else:
                        uom_base_price = price_change_pool.new_price

                    if not self.uom_id.uom_type == "reference":
                        return uom_base_price * self.uom_id.factor_inv
                    else:
                        return uom_base_price
            else:
                return price_change_pool.new_price

        return 0.00
