from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProformaInvoice(models.Model):
    _name = 'proforma.invoice'
    _description = 'Proforma Invoice (PI)'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _order = 'id DESC'
    _rec_name = 'name'

    name = fields.Char(string='Name', index=True, readonly=True, default="/")
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True,
                                 readonly=True, states={'draft': [('readonly', False)]})
    invoice_date = fields.Date('Invoice Date', readonly=True, required=1, states={'draft': [('readonly', False)]})
    advising_bank_id = fields.Many2one('res.bank', string='Advising Bank', required=True, readonly=True,
                                       states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, required=True,
                                  states={'draft': [('readonly', False)]}, track_visibility='onchange')

    beneficiary_id = fields.Many2one('res.company', string='Beneficiary', required=True, readonly=True,
                                     states={'draft': [('readonly', False)]})

    transport_by = fields.Char(string='Transport By', required=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    terms_condition = fields.Text(string='Terms & Conditions', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    terms_id = fields.Many2one('terms.setup', string='Terms', store=False, readonly=True,
                               states={'draft': [('readonly', False)]})

    """ Shipping Address"""
    ship_freight_type = fields.Char(string='Freight Type', readonly=True, states={'draft': [('readonly', False)]})
    ship_exp_date = fields.Char(string='Exp. Shipping Date', readonly=True, states={'draft': [('readonly', False)]})
    ship_exp_good_weight = fields.Char(string='Exp. Goods Weight', readonly=True,
                                       states={'draft': [('readonly', False)]})
    ship_exp_cubic_weight = fields.Char(string='Exp. Cubic Weight', readonly=True,
                                        states={'draft': [('readonly', False)]})
    ship_total_pkg = fields.Char(string='Total Package', readonly=True, states={'draft': [('readonly', False)]})

    """ Customer Address"""
    customer_add = fields.Text(string='Customer Address', readonly=True, compute='_compute_customer_address')

    """ Ship To"""
    terms_condition = fields.Text(string='Terms of Condition', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    packing = fields.Char(string='Packing', required=True, readonly=True, states={'draft': [('readonly', False)]})
    terms_of_payment = fields.Char(string='Terms Of Payment', required=True, readonly=True,
                                   states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed")
    ], default='draft', track_visibility='onchange')

    sequence_id = fields.Char('Sequence', readonly=True)

    """ Calculations fields after """
    sub_total = fields.Float(string='Sub Total', readonly=True)
    taxable_amount = fields.Float(string='Taxable Amount')
    untaxaed_amount = fields.Float(string='Untaxed Amount', readonly=True)
    taxed_amount = fields.Float(string='Tax', readonly=True)
    freight_charge = fields.Float(string='Freight Charge', readonly=True, states={'draft': [('readonly', False)]},
                                  track_visibility='onchange')
    total = fields.Float(string='Total', readonly=True, track_visibility='onchange')

    """ Relational field"""
    line_ids = fields.One2many('proforma.invoice.line', 'pi_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]})

    def _get_pack_type(self):
        return self.env['product.packaging.mode'].search([], limit=1)

    """New field"""
    pack_type = fields.Many2one('product.packaging.mode', string='Packing Mode', default=_get_pack_type,
                                readonly=True,
                                states={'draft': [('readonly', False)]}
                                , required=True)

    credit_sales_or_lc = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sales Type', readonly=True,
        states={'draft': [('readonly', False)]}, required=True)

    def _get_order_type(self):
        return self.env['sale.order.type'].search([], limit=1)

    type_id = fields.Many2one(comodel_name='sale.order.type', string='Type', default=_get_order_type, readonly=True,
                              states={'draft': [('readonly', False)]}, track_visibility='onchange')

    """On Change fucn"""

    @api.onchange('type_id')
    def onchange_type(self):
        sale_type_pool = self.env['sale.order.type'].search([('id', '=', self.type_id.id)])
        if self.type_id:
            self.credit_sales_or_lc = sale_type_pool.sale_order_type
            self.currency_id = sale_type_pool.currency_id.id

    @api.multi
    @api.onchange('currency_id')
    def currency_id_onchange(self):
        self._get_changed_price()

    @api.multi
    @api.onchange('pack_type')
    def pack_type_onchange(self):
        self._get_changed_price()

    def _get_changed_price(self):
        for order in self:
            for line in order.line_ids:
                line._set_product_line()

        """On Change fucn ends"""

    @api.multi
    def _compute_customer_address(self, context=None):
        if self.partner_id:
            str_address = self.getAddressByPartner(self.partner_id)
            self.customer_add = str_address

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
                        avg_unit_price = total_price_subtotal / (
                            total_qty * 1.0)  # to ensure flaot value multily with 1.0

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

        sub_total = 0
        total = 0

        for v in vals.get('line_ids'):
            sub_total += v[2]['price_unit'] * v[2]['quantity']
            total += v[2]['price_unit'] * v[2]['quantity']

        vals['sub_total'] = sub_total
        vals['total'] = total

        return super(ProformaInvoice, self).create(vals)

    @api.multi
    def write(self, vals, context=None):
        sub_total = 0
        total = 0

        for line in self.line_ids:
            sub_total += line['price_subtotal']
            total += line['price_subtotal']

        vals['sub_total'] = sub_total
        vals['total'] = total

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
            if self.beneficiary_id and self.beneficiary_id != so.company_id:
                raise ValidationError('Please add Sale Order whose Beneficiary is same.')
            elif self.operating_unit_id and self.operating_unit_id != so.operating_unit_id:
                raise ValidationError('Please add Sale Order whose Unit is same.')
            elif self.partner_id and self.partner_id != so.partner_id:
                raise ValidationError('Please add Sale Order whose Customer is same.')
            elif self.currency_id and self.currency_id != so.currency_id:
                raise ValidationError('Please add Sale Order whose Currency is same.')
            else:
                self.beneficiary_id = so.company_id
                self.operating_unit_id = so.operating_unit_id
                self.partner_id = so.partner_id
                self.currency_id = so.currency_id
                self.customer_add = self.getAddressByPartner(so.partner_id)

            sub_total += so.amount_untaxed
            taxed_amount += so.amount_tax
            total += so.amount_total
            untaxed_amount += so.amount_untaxed

        self.line_ids = self._prepare_lines_by_so_ids(self.so_ids)

        self.sub_total = sub_total
        self.taxed_amount = taxed_amount
        self.total = total
        self.untaxed_amount = untaxed_amount

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

        # self.update_Pi_to_so_obj()
        res = {'state': 'confirm'}
        team = self.env['crm.team']._get_default_team_id()

        new_seq = self.env['ir.sequence'].next_by_code_new('proforma.invoice', self.invoice_date, team.operating_unit_id)
        if new_seq:
            res['name'] = new_seq

        sub_total = 0
        total = 0

        for line in self.line_ids:
            sub_total += line.price_unit * line.quantity
            total += line.price_unit * line.quantity

        res['sub_total'] = sub_total
        res['total'] = total

        self.write(res)

    def update_Pi_to_so_obj(self):
        # Update PI to SO
        for so in self.so_ids:
            so.pi_id = self.id

            # update DA
            da_obj = so.env['delivery.authorization'].search([('sale_order_id', '=', so.id)])
            if da_obj:
                for da_ in da_obj:
                    da_.pi_id = self.id  # update PI to DA if it is already created

            # update DO
            do_obj = so.env['delivery.order'].search([('sale_order_id', '=', so.id)])
            if do_obj:
                for do_ in do_obj:
                    do_.pi_id = self.id  # update PI to DO if it is already created

    @api.onchange('freight_charge')
    def onchange_freight_charge(self):
        if self.freight_charge < 0:
            raise UserError('Freight Charge can not be Negative')

        if self.freight_charge:
            self.total = self.total + self.freight_charge

    @api.onchange('terms_id')
    def onchange_terms_id(self):
        if self.terms_id:
            self.terms_condition = self.terms_id.terms_condition

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
    @api.model
    def _default_operating_unit(self):
        team = self.env['crm.team']._get_default_team_id()
        if team.operating_unit_id:
            return team.operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',
                                        required=True, readonly=True,
                                        default=_default_operating_unit, track_visibility='onchange')

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


class ProformaInvoiceLine(models.Model):
    _name = 'proforma.invoice.line'
    _description = 'Proforma Invoice Line (PI Line)'

    """ Line values"""
    product_id = fields.Many2one('product.product', string="Product", required=True)
    description = fields.Char(string='Description', required=True)
    uom_id = fields.Many2one('product.uom', string="Unit of Measure", required=True)
    quantity = fields.Float(string="Ordered Qty")
    price_unit = fields.Float(string="Unit Price", required=True)
    tax = fields.Many2one('account.tax', string='Taxes')
    price_subtotal = fields.Float(string="Sub Total", readonly=False)

    """ Relational field"""
    pi_id = fields.Many2one('proforma.invoice', ondelete='cascade')

    def _set_product_line(self):
        if self.product_id:
            self.price_unit = self._get_product_sales_price(self.product_id)

            self.description = self.product_id.name + ' (' + self.product_id.attribute_value_ids.name + ')'
            self.quantity = 1
            self.price_subtotal = self.price_unit * self.quantity

            self.pi_id.sub_total = self.price_subtotal
            self.pi_id.taxed_amount = self.calculate_tax_amount(self.tax.id, self.price_subtotal)
            self.pi_id.untaxaed_amount = self.price_subtotal
            self.pi_id.total = self.pi_id.taxed_amount + self.price_subtotal

    @api.onchange('product_id')
    def onchange_product_id(self):
        self._set_product_line()

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.quantity < 0:
            raise UserError('Quantity can not be Negative')

        self.price_subtotal = self.price_unit * self.quantity

        ## Set Proforma Invoice Table value
        # self.pi_id.currency_id.id = active_prod_price_pool.currency_id.id
        self.pi_id.sub_total = self.price_subtotal
        self.pi_id.taxed_amount = self.calculate_tax_amount(self.tax.id, self.price_subtotal)
        self.pi_id.untaxed_amount = self.price_subtotal
        self.pi_id.total = self.pi_id.taxed_amount + self.price_subtotal

    @api.onchange('uom_id')
    def onchange_uomid(self):
        self._set_product_line()

    def calculate_tax_amount(self, tax_id, total_price):
        if tax_id:
            tax_pool = self.env['account.tax'].search([('id', '=', tax_id)])
            return (tax_pool.amount / 100) * total_price

    def _get_product_sales_price(self, product):

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
