from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import amount_to_text_en
import time


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_this_so_payment_check = fields.Boolean(string='is_this_so_payment_check',default=False)

    def _get_order_type(self):
        return self.env['sale.order.type'].search([], limit=1)

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, track_visibility='onchange',
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))

    type_id = fields.Many2one(comodel_name='sale.order.type', string='Type', default=_get_order_type, readonly=True,
                              states={'to_submit': [('readonly', False)]})

    currency_conversion_rate = fields.Float(string='Conversion Rate', readonly=True,
                                            states={'to_submit': [('readonly', False)]})

    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', readonly=True, copy=True)
    incoterm = fields.Many2one('stock.incoterms', 'Incoterms', readonly=True,
                               help="International Commercial Terms are a series of predefined commercial terms used in international transactions.",
                               states={'to_submit': [('readonly', False)]})
    client_order_ref = fields.Char(string='Customer Reference', copy=False, readonly=True,
                                   states={'to_submit': [('readonly', False)]})
    team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, readonly=True, default=_get_default_team,
                              oldname='section_id')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user, readonly=True, )
    fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position',
                                         readonly=True, states={'to_submit': [('readonly', False)]})
    origin = fields.Char(string='Source Document',
                         help="Reference of the document that generated this sales order request.", readonly=True,
                         states={'to_submit': [('readonly', False)]})

    credit_sales_or_lc = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
        ('tt_sales', 'TT'),
        ('contract_sales', 'Sales Contract'),
    ], string='Sales Type', readonly=True, related='type_id.sale_order_type')

    delivery_mode = fields.Selection([('cnf','C&F'),('fob','FOB')], string='Delivery Mode')
    vat_mode = fields.Selection([('vat','VAT'),('non_vat','Non VAT')], string='Is VAT Applicable')
    bonded_mode = fields.Selection([('bonded','Bonded'),('non_bonded','Non Bonded')], string='Is Bonded Applicable')

    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True,
                                 states={'to_submit': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', track_visibility='onchange')

    # inherited fields from sale
    partner_id = fields.Many2one('res.partner', string='Customer', required=True,
                                 change_default=True, index=True, track_visibility='always')
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', required=True,
                                         domain="[('parent_id','=',partner_id),('type','=','invoice')]",
                                         help="Invoice address for current sales order.")
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', required=True,
                                          domain="[('parent_id','=',partner_id),('type','=','delivery')]",
                                          help="Delivery address for current sales order.")

    comment = fields.Char(string='Approval Causes', track_visibility='onchange')

    # ..............................
    # terms_setup_id = fields.Many2one('terms.setup', string='Payment Days', readonly=True, track_visibility='onchange',
    #                                 states={'to_submit': [('readonly', False)]})
    #
    # freight_mode = fields.Selection([
    #     ('fob', 'FOB'),
    #     ('c&f', 'C&F')
    # ], string='Freight Mode', default='fob', readonly=True, track_visibility='onchange',
    #                                 states={'to_submit': [('readonly', False)]})



    @api.model
    def _default_note(self):
        return self.env.user.company_id.sale_note

    note = fields.Text('Terms and conditions', default=_default_note, readonly=True,
                       states={'to_submit': [('readonly', False)]})

    state = fields.Selection([
        ('to_submit', 'Draft'),
        ('draft', 'Sales Approval'),
        ('submit_quotation', 'Validate'),
        ('validate', 'Accounts Approval'),
        ('sent', 'CXO Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='to_submit')

    def _get_pack_type(self):
        return self.env['product.packaging.mode'].search([], limit=1)

    pack_type = fields.Many2one('product.packaging.mode', string='Packing Mode', default=_get_pack_type, required=True)
    currency_id = fields.Many2one("res.currency", related='type_id.currency_id', required=False, string="Currency")

    picking_policy = fields.Selection([
        ('direct', 'Deliver each product when available'),
        ('one', 'Deliver all products at once')],
        string='Shipping Policy', required=True, readonly=True, default='direct',
        states={'to_submit': [('readonly', False)]})

    project_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True,
                                 states={'to_submit': [('readonly', False)]},
                                 help="The analytic account related to a sales order.", copy=False)

    region_type = fields.Selection([('local', "Local"), ('foreign', "Foreign")], readonly=True, required=True)

    """ PI and LC """
    pi_id = fields.Many2one('proforma.invoice', string='PI Ref. No.',
                            readonly=True, states={'to_submit': [('readonly', False)]})
    # domain = [('credit_sales_or_lc', '=', 'lc_sales'), ('state', '=', 'confirm')],
    lc_id = fields.Many2one('letter.credit', string='LC Ref. No.', track_visibility='onchange', readonly=True)

    # remaining_credit_limit = fields.Char(string="Customer's Remaining Credit Limit", track_visibility='onchange')

    fields_readonly = fields.Boolean('Fields Readonly or not?', default=False)

    """ Update is_commission_generated flag to False """

    @api.model
    def create(self, vals):

        sales_channel_obj = self.env['sales.channel'].search([('id', '=', vals['sales_channel'])])

        vals['approver_user_id'] = sales_channel_obj.user_id.id
        vals['warehouse_id'] = sales_channel_obj.warehouse_id.id
        vals['operating_unit_id'] = sales_channel_obj.operating_unit_id.id

        # to call the Draft SO Seq
        new_seq = self.env['ir.sequence'].next_by_code('sale.order') or '/'
        if new_seq:
            vals['name'] = new_seq

        if vals['pi_id']:
            pi_pool = self.env['proforma.invoice'].search([('id', '=', vals['pi_id'])])
            vals['partner_id'] = pi_pool.partner_id.id
            invoice_ids = pi_pool.partner_id.child_ids.filtered(lambda x: x.type == 'invoice')
            shipping_ids = pi_pool.partner_id.child_ids.filtered(lambda x: x.type == 'delivery')
            if invoice_ids:
                vals['partner_invoice_id'] = invoice_ids[0].id
            else:
                vals['partner_invoice_id'] = pi_pool.partner_id.id
            if shipping_ids:
                vals['partner_shipping_id'] = shipping_ids[0].id
            else:
                vals['partner_shipping_id'] = pi_pool.partner_id.id

                # vals['partner_invoice_id'] = pi_pool.partner_id.child_ids.filtered(lambda x: x.type == 'invoice').id or pi_pool.partner_id.id
                # vals['partner_shipping_id'] = pi_pool.partner_id.child_ids.filtered(lambda x: x.type == 'delivery').id or pi_pool.partner_id.id

        return super(SaleOrder, self).create(vals)

    @api.multi
    def write(self, vals):

        if 'sales_channel' in vals:
            sales_channel_obj = self.env['sales.channel'].search([('id', '=', vals['sales_channel'])])

            vals['approver_user_id'] = sales_channel_obj.user_id.id
            vals['warehouse_id'] = sales_channel_obj.warehouse_id.id
            vals['operating_unit_id'] = sales_channel_obj.operating_unit_id.id

        if 'pi_id' in vals:
            pi_pool = self.env['proforma.invoice'].search([('id', '=', vals['pi_id'])])
            vals['partner_id'] = pi_pool.partner_id.id
            invoice_ids = pi_pool.partner_id.child_ids.filtered(lambda x: x.type == 'invoice')
            shipping_ids = pi_pool.partner_id.child_ids.filtered(lambda x: x.type == 'delivery')
            if invoice_ids:
                vals['partner_invoice_id'] = invoice_ids[0].id
            else:
                vals['partner_invoice_id'] = pi_pool.partner_id.id
            if shipping_ids:
                vals['partner_shipping_id'] = shipping_ids[0].id
            else:
                vals['partner_shipping_id'] = pi_pool.partner_id.id

        return super(SaleOrder, self).write(vals)

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create()
        self.invoice_ids.write({'is_commission_generated': False})
        return res

    @api.depends('order_line.da_qty')
    def _da_button_show_hide(self):
        for sale_orders in self:
            for sale_line in sale_orders.order_line:
                if sale_line.da_qty == 0.00:
                    sale_orders.da_btn_show_hide = True
                else:
                    sale_orders.da_btn_show_hide = False
                    break;

    da_btn_show_hide = fields.Boolean(string="Is DA btn visible", compute="_da_button_show_hide", store=True)

    @api.multi
    def amount_to_word(self, number):
        if self.currency_id.name.encode('ascii', 'ignore') == 'BDT':
            return self.env['res.currency'].amount_to_word(float(number))
        else:
            currency = self.currency_id.name.encode('ascii', 'ignore')
            return amount_to_text_en.amount_to_text(number, 'en', currency)

    @api.multi
    def action_reset(self):
        self.state = 'to_submit'

    @api.multi
    def action_validate(self):
        self.state = 'sent'

    @api.multi
    def action_to_submit(self):
        for orders in self:

            if orders.region_type == False:
                raise UserError('You Cannot Submit this SO due to Region Type is missing.')

            # Check seq needs to re-generate or not
            if orders.operating_unit_id.name not in orders.name:
                new_seq = orders.env['ir.sequence'].next_by_code_new('sale.order', self.create_date,
                                                                     orders.operating_unit_id) or '/'

                if new_seq:
                    orders.name = new_seq

            if orders.validity_date:
                expiration_date = orders.validity_date + ' 23:59:59'
                if expiration_date <= orders.date_order:
                    raise UserError('Expiration Date can not be less than Order Date')

            orders.state = 'draft'

    @api.onchange('type_id')
    def _onchange_type_id(self):
        if self.type_id:
            sale_type_pool = self.env['sale.order.type'].search([('id', '=', self.type_id.id)])
            self.credit_sales_or_lc = sale_type_pool.sale_order_type
            self.currency_id = sale_type_pool.currency_id.id

            # if self.type_id.sale_order_type != 'lc_sales' and \
            #                 self.type_id.sale_order_type != 'tt_sales' and \
            #                 self.type_id.sale_order_type != 'contract_sales':
            #     self.pi_id = None

            self.pi_id = None
            self.payment_term_id = None

            if self.type_id.sale_order_type == 'lc_sales' or \
                    self.type_id.sale_order_type == 'tt_sales' or \
                    self.type_id.sale_order_type == 'contract_sales':
                existing_lc = self.search([('type_id', '=', self.type_id.id)])
                return {'domain': {'pi_id': [('id', 'not in', [i.pi_id.id for i in existing_lc]),
                                             ('type_id', '=', self.type_id.id), ('state', '=', 'confirm')]}}
            else:
                self.fields_readonly = False

    @api.multi
    def _is_double_validation_applicable(self):
        for orders in self:
            for lines in orders.order_line:
                cust_commission_pool = orders.env['customer.commission'].search(
                    [('customer_id', '=', orders.partner_id.id), ('product_id', '=', lines.product_id.ids)])

                price_change_pool = self.env['product.sale.history.line'].search(
                    [('product_id', '=', lines.product_id.id),
                     ('currency_id', '=', lines.currency_id.id),
                     ('product_package_mode', '=', orders.pack_type.id),
                     ('uom_id', '=', lines.product_uom.id)])

                discounted_product_price = price_change_pool.new_price - price_change_pool.discount

                if orders.credit_sales_or_lc == 'lc_sales' or orders.credit_sales_or_lc == 'tt_sales' or orders.credit_sales_or_lc == 'contract_sales':

                    if price_change_pool.new_price >= lines.price_unit and lines.price_unit >= discounted_product_price:
                        return False  # Single Validation

                    # If LC and PI ref is present, go to the Final Approval, Else go to Second level approval
                    if orders.lc_id and orders.pi_id:
                        for coms in cust_commission_pool:
                            if lines.commission_rate != coms.commission_rate or \
                                            lines.price_unit < discounted_product_price or lines.price_unit > discounted_product_price:
                                return True  # Go to two level approval process
                                break;

                            return False  # One level approval process
                    elif orders.pi_id and not orders.lc_id:
                        return True  # Go to two level approval process
                    else:
                        return False  # Go to two level approval process

                elif orders.credit_sales_or_lc == 'credit_sales':

                    partner_pool = orders.partner_id

                    account_receivable = abs(partner_pool.credit)
                    sales_order_amount_total = orders.amount_total

                    unpaid_tot_inv_amt = orders.unpaid_total_invoiced_amount()
                    undelivered_tot_do_amt = orders.undelivered_do_qty_amount()

                    customer_total_credit = account_receivable + sales_order_amount_total + unpaid_tot_inv_amt + undelivered_tot_do_amt
                    customer_credit_limit = partner_pool.credit_limit

                    if price_change_pool.new_price >= lines.price_unit and lines.price_unit >= discounted_product_price:
                        return False  # Single Validation

                    for coms in cust_commission_pool:
                        if (abs(customer_total_credit) > customer_credit_limit
                            or lines.commission_rate != coms.commission_rate
                            or lines.price_unit < discounted_product_price or lines.price_unit > discounted_product_price):

                            return True
                            break;
                        else:
                            return False

        for lines in orders.order_line:
            product_pool = orders.env['product.product'].search([('id', '=', lines.product_id.ids)])
            if lines.price_unit != product_pool.list_price:
                return True  # Go to two level approval process
            else:
                return False  # One level approval process

    double_validation = fields.Boolean('Apply Double Validation', compute="_is_double_validation_applicable")

    # Total DO Qty amount which is not delivered yet
    @api.multi
    def undelivered_do_qty_amount(self):
        tot_undelivered_amt = 0
        for stock in self:
            # picking_type_id.code "outgoing" means: Customer
            stock_pick_pool = stock.env['stock.picking'].search([('picking_type_id.code', '=', 'outgoing'),
                                                                 ('picking_type_id.name', '=', 'Delivery Orders'),
                                                                 ('partner_id', '=', stock.partner_id.id),
                                                                 ('state', '!=', 'done')])

            stock_amt_list = []
            for stock_pool in stock_pick_pool:
                # We assume that delivery_order_id will never be null,
                # but to avoid garbage data added this extra checking
                if stock_pool.delivery_order_id:
                    for so_line in stock.order_line:
                        for prod_op_ids in stock_pool.pack_operation_product_ids:
                            unit_price = so_line.price_unit
                            product_qty = prod_op_ids.product_qty
                            stock_amt_list.append(unit_price * product_qty)

                tot_undelivered_amt = sum(stock_amt_list)

        return tot_undelivered_amt

    ## Total Invoiced amount which is not in Paid state
    @api.multi
    def unpaid_total_invoiced_amount(self):
        for invc in self:
            acc_invoice_pool = invc.env['account.invoice'].search([('journal_id.type', '=', 'sale'),
                                                                   ('partner_id', '=', invc.partner_id.id),
                                                                   ('state', '=', 'draft')])

            total_list = []
            for inv_ in acc_invoice_pool:
                total_list.append(inv_.amount_total)

            total_unpaid_amount = sum(total_list)

        return total_unpaid_amount

    @api.multi
    def action_submit(self):

        is_double_validation = False
        causes = []

        for order in self:
            partner_pool = order.partner_id
            for lines in order.order_line:

                cust_commission_pool = order.env['customer.commission'].search(
                    [('currency_id', '=', order.currency_id.id), ('customer_id', '=', order.partner_id.id),
                     ('product_id', '=', lines.product_id.ids)], limit=1)

                commission_rate = cust_commission_pool.commission_rate if cust_commission_pool else 0

                price_change_pool = order.env['product.sale.history.line'].search(
                    [('product_id', '=', lines.product_id.id),
                     ('currency_id', '=', lines.currency_id.id),
                     ('product_package_mode', '=', order.pack_type.id),
                     ('uom_id', '=', lines.product_uom.id)], limit=1)

                is_double_validation = order.check_second_approval(commission_rate , lines, price_change_pool, causes)

                if order.credit_sales_or_lc == 'credit_sales':

                    account_receivable = partner_pool.credit
                    sales_order_amount_total = order.amount_total

                    unpaid_tot_inv_amt = order.unpaid_total_invoiced_amount()
                    undelivered_tot_do_amt = order.undelivered_do_qty_amount()

                    customer_total_credit = account_receivable + sales_order_amount_total + undelivered_tot_do_amt + unpaid_tot_inv_amt
                    customer_credit_limit = partner_pool.credit_limit

                    if abs(customer_total_credit) > customer_credit_limit:
                        causes.append("Customer crossed his Credit Limit. Current Credit Limit is " + str(abs(customer_credit_limit)))
                        is_double_validation = True


        if is_double_validation:
            comment_str = "Acceptance needs for " + str(len(causes)) + " cause(s) which are: "
            comment_str += " & ".join(causes)
            order.write({'state': 'validate', 'comment':comment_str})  # Go to two level approval process

        else:
            self._automatic_delivery_authorization_creation()
            order.write({'state': 'done'})  # One level approval process

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self._automatic_delivery_authorization_creation()

        return res

    @api.multi
    def _automatic_delivery_authorization_creation(self):
        # System confirms that one Sale Order will have only one DA & DO, so check with Sales Order ID
        sale_obj = self.env['delivery.authorization'].search([('sale_order_id', '=', self.id)])

        if not sale_obj:
            vals = {
                'sale_order_id': self.id,
                'deli_address': self.partner_shipping_id.name,
                'currency_id': self.type_id.currency_id,
                'parent_id': self.partner_id,
                'so_type': self.credit_sales_or_lc,
                'so_date': self.date_order,
                # 'warehouse_id': self.warehouse_id,
                'amount_untaxed': self.amount_total,
                'tax_value': self.amount_tax,
                'total_amount': self.amount_total,
                'operating_unit_id': self.operating_unit_id.id
            }

            da_pool = self.env['delivery.authorization'].create(vals)

            for record in self.order_line:
                da_line = {
                    'parent_id': da_pool.id,
                    'product_id': record.product_id.id,
                    'quantity': record.product_uom_qty,
                    'pack_type': self.pack_type.id,
                    'uom_id': record.product_uom.id,
                    'price_unit': record.price_unit,
                    'commission_rate': record.commission_rate,
                    'price_subtotal': record.price_total,
                    'tax_id': record.tax_id.id,
                    'delivery_qty': record.product_uom_qty,
                    'sale_order_id': self.id,
                }

                self.env['delivery.authorization.line'].create(da_line)

    def action_view_delivery_auth(self):
        form_view = self.env.ref('delivery_order.delivery_order_form')
        action = self.env.ref('delivery_order.delivery_order_action').read()[0]
        da_pool = self.env['delivery.authorization'].search([('sale_order_id', '=', self.id)])

        if len(da_pool) > 1:
            action['domain'] = [('id', 'in', da_pool.ids)]
        elif da_pool:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = da_pool.id

        return action


    def check_second_approval(self, commission_rate, lines, price_change_pool, causes):

        is_double_validation = False

        if commission_rate == 0 and lines.commission_rate:
            causes.append("There are no existing commission for this product, but requested commission is "+ str(lines.commission_rate))
            is_double_validation = True

        if commission_rate > 0 and lines.commission_rate != commission_rate:
            causes.append(
                "Existing Commission rate is " + str(commission_rate) + ", but requested Commission rate is " + str(lines.commission_rate))
            is_double_validation = True


        if len(price_change_pool) == 0 and lines.price_unit:
            causes.append("There are no existing price for this product, but requested price is "+ str(lines.price_unit))
            is_double_validation = True

        for price_history in price_change_pool:
            discounted_product_price = price_history.new_price - price_history.discount

            if lines.price_unit not in range(int(discounted_product_price), int(price_history.new_price + 1)):
                causes.append(
                    "Existing Approve Price is " + str(price_history.new_price) + ", but requested Price is " + str(lines.price_unit) + ". Which may not cover with discounted price.")
                is_double_validation = True

        return is_double_validation

    # def second_approval_business_logics(self, cust_commission_pool, lines, price_change_pool):
    #
    #     if len(price_change_pool) == 0 and lines.price_unit:
    #         return True  # second approval
    #
    #     if len(cust_commission_pool) == 0 and lines.commission_rate:
    #         return True  # second approval
    #
    #     for coms in cust_commission_pool:
    #         if price_change_pool.currency_id.id == lines.currency_id.id:
    #             for price_history in price_change_pool:
    #                 discounted_product_price = price_history.new_price - price_history.discount
    #
    #                 if lines.commission_rate != coms.commission_rate:
    #                     return True
    #
    #                 if price_history.new_price >= lines.price_unit and lines.price_unit >= discounted_product_price:
    #                     return False  # Single Validation
    #
    #                 if lines.commission_rate != coms.commission_rate or \
    #                         (lines.price_unit < discounted_product_price
    #                          or lines.price_unit > discounted_product_price):
    #                     return True
    #                     break;
    #                 else:
    #                     return False

    @api.multi
    def action_create_delivery_order(self):
        view = self.env.ref('delivery_order.delivery_order_form')

        return {
            'name': ('Delivery Authorization'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'delivery.authorization',
            'view_id': [view.id],
            'type': 'ir.actions.act_window',
            'context': {'default_sale_order_id': self.id},
        }

    @api.multi
    @api.onchange('currency_id')
    def currency_id_onchange(self):
        self._get_changed_price()

    @api.multi
    @api.onchange('pack_type')
    def pack_type_onchange(self):
        if not self.pi_id:
            self._get_changed_price()

    def _get_changed_price(self):
        for order in self:
            for line in order.order_line:
                vals = {}
                if line.product_id:
                    vals['price_unit'] = line._get_product_sales_price(line.product_id)
                    line.update(vals)

    @api.onchange('pi_id')
    def _onchange_pi_id(self):
        if self.pi_id:
            val = []
            pi_pool = self.env['proforma.invoice'].search([('id', '=', self.pi_id.id)])
            self.partner_id = pi_pool.partner_id
            self.pack_type = pi_pool.pack_type
            self.payment_term_id = pi_pool.account_payment_term_id

            for record in pi_pool.line_ids:
                commission = self.env['customer.commission'].search(
                    [('customer_id', '=', self.partner_id.id), ('product_id', '=', record.product_id.id),
                     ('status', '=', True)])

                if commission:
                    for coms in commission:
                        self.commission_rate = coms.commission_rate
                else:
                    self.commission_rate = 0

                val.append((0, 0, {'product_id': record.product_id.id,
                                   'name': record.product_id.name,
                                   'product_uom_qty': record.quantity,
                                   'product_uom': record.uom_id.id,
                                   'price_unit': record.price_unit,
                                   'commission_rate': self.commission_rate,
                                   'price_subtotal': record.price_subtotal,
                                   # 'tax_id': record.tax.id,
                                   'da_qty': record.quantity,  # this value is set to show hide DA Create Button on SO

                                   }))

            self.order_line = val
            self.fields_readonly = True

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.pi_id:
            pi_pool = self.env['proforma.invoice'].search([('id', '=', self.pi_id.id)])
            self.payment_term_id = pi_pool.account_payment_term_id

    @api.model
    def _default_operating_unit(self):
        team = self.env['crm.team']._get_default_team_id()
        if team.operating_unit_id:
            return team.operating_unit_id
        else:
            return self.env.user.default_operating_unit_id

    def _get_sales_channel(self):
        return self.env['sales.channel'].search([], limit=1)

    sales_channel = fields.Many2one('sales.channel', string='Sales Channel', readonly=True, track_visibility='onchange',
                                    states={'to_submit': [('readonly', False)]}, required=True, default=_get_sales_channel)

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', track_visibility='onchange',
        required=True, states={'to_submit': [('readonly', True)],
                               'draft': [('readonly', True)], 'submit_quotation': [('readonly', True)]},
    )

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit', track_visibility='onchange',
        required=True, states={'to_submit': [('readonly', True)],
                               'draft': [('readonly', True)], 'submit_quotation': [('readonly', True)]}, )

    approver_user_id = fields.Many2one('res.users', string='Approver Manager', track_visibility='onchange')

    @api.onchange('sales_channel')
    def _onchange_sales_channel(self):
        self.warehouse_id = self.sales_channel.warehouse_id.id
        self.warehouse_id = self.sales_channel.warehouse_id.id
        self.operating_unit_id = self.sales_channel.operating_unit_id.id
        self.approver_user_id = self.sales_channel.user_id.id

    # Ovrride this entire mentod and did not call super.
    # Where ever this method is called, not impact on business
    @api.multi
    @api.constrains('team_id', 'operating_unit_id')
    def _check_team_operating_unit(self):
        for rec in self:
            if rec.pi_id:
                if rec.operating_unit_id != rec.pi_id.operating_unit_id:
                    raise ValidationError(_('Configuration error\n'
                                            'The Operating Unit of the Proforma Invoice (PI) '
                                            'must match with that of the '
                                            'Quotation/Sales Order'))

            if (rec.team_id and rec.team_id.operating_unit_id != rec.operating_unit_id):
                continue;

    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        domain = []
        if users_obj.has_group('gbs_application_group.group_cxo'):
            domain = [
                ('state', 'in', ['sent'])]
            return domain
        elif users_obj.has_group('gbs_application_group.group_head_account'):
            domain = [
                ('state', 'in', ['validate'])]
            return domain
        elif users_obj.has_group('gbs_application_group.group_head_sale'):

            domain = [
                ('state', 'in', ['draft']), ('approver_user_id', '=', self.env.user.id)]
            return domain
        else:
            return False

        return domain

    @api.constrains('order_line')
    def _check_multiple_products_line(self):
        if len(self.order_line) > 1:
            raise ValidationError("You can't add multiple products")

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('to_submit', 'cancel'):
                raise UserError(_('You can not delete a sent quotation or a sales order! Try to cancel it before.'))
        return super(SaleOrder, self).unlink()

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()

        res['currency_id'] = self.currency_id.id
        res['cost_center_id'] = self.order_line[0].product_id.cost_center_id.id

        return res


################################
# Sale Order Line Class
################################
class InheritedSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    da_qty = fields.Float(string='DA Qty.', default=0)


    @api.one
    @api.constrains('product_uom_qty', 'commission_rate')
    def _check_order_line_inputs(self):
        if self.product_uom_qty or self.commission_rate or self.price_unit:
            if self.product_uom_qty < 0 or self.commission_rate < 0 or self.price_unit < 0:
                raise ValidationError('Price Unit, Ordered Qty & Commission Rate can not be Negative value')

            if self.order_id.product_id.commission_type == 'percentage':
                if self.commission_rate > 100:
                    raise ValidationError('Commission Rate can not be greater than 100')

    def _get_product_sales_price(self, product):

        if product:
            price_change_pool = self.env['product.sale.history.line'].search(
                [('product_id', '=', product.id),
                 ('currency_id', '=', self.order_id.currency_id.id),
                 ('product_package_mode', '=', self.order_id.pack_type.id),
                 #('country_id','=', self.order_id.partner_id.country_id.id),
                 #('terms_setup_id.days','=',self.order_id.terms_setup_id.days),
                 #('freight_mode', '=', self.order_id.freight_mode),
                 ('uom_id', '=', self.product_uom.id)])

            if not price_change_pool:
                price_change_pool = self.env['product.sale.history.line'].search(
                    [('product_id', '=', product.id),
                     ('currency_id', '=', self.order_id.currency_id.id),
                     ('product_package_mode', '=', self.order_id.pack_type.id),
                     # ('country_id', '=', self.order_id.partner_id.country_id.id),
                     # ('terms_setup_id.days', '=', self.order_id.terms_setup_id.days),
                     # ('freight_mode','=',self.order_id.freight_mode),
                     ('category_id', '=', self.product_uom.category_id.id)])

                if price_change_pool:
                    if not price_change_pool.uom_id.uom_type == "reference":
                        uom_base_price = price_change_pool.new_price / price_change_pool.uom_id.factor_inv
                    else:
                        uom_base_price = price_change_pool.new_price

                    if not self.product_uom.uom_type == "reference":
                        return uom_base_price * self.product_uom.factor_inv
                    else:
                        return uom_base_price
            else:
                return price_change_pool.new_price

        return 0.00

    @api.multi
    @api.onchange('product_id', 'currency_id', 'pack_type')
    def product_id_change(self):

        res = super(InheritedSaleOrderLine, self).product_id_change()
        vals = {}

        if self.product_id:
            vals['price_unit'] = self._get_product_sales_price(self.product_id)
            self.update(vals)

        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(InheritedSaleOrderLine, self).product_uom_change()
        #self.da_qty = self.product_uom_qty

        vals = {}
        if self.product_id and not self.price_unit:
            vals['price_unit'] = self._get_product_sales_price(self.product_id)
            self.update(vals)

        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(InheritedSaleOrderLine, self)._prepare_invoice_line(qty)
        res['cost_center_id'] = self.product_id.cost_center_id.id
        return res


########################
# Sales team class
#######################
class CrmTeam(models.Model):
    _inherit = 'crm.team'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    user_id = fields.Many2one('res.users', string='Team Leader', required=True)

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['crm.team'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError('Sales Team for this given Name already exists')

    @api.multi
    def unlink(self):
        for crm in self:
            raise UserError('You can not delete Sales Team after creation')
        return super(CrmTeam, self).unlink()


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['product.attribute'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError('Attribute name must be unique!')


class ProductUom(models.Model):
    _inherit = "product.uom"

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['product.uom'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError(" Unit of Measure's name must be unique!")


class ProductTags(models.Model):
    _inherit = "res.partner.category"

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['res.partner.category'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError(" Contact Tags's name must be unique!")


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['product.category'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError("Product Category's name must be unique!")


class ProductUomCategory(models.Model):
    _inherit = 'product.uom.categ'

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['product.uom.categ'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError("Product Uom Category's name must be unique!")


class Bank(models.Model):
    _inherit = 'res.bank'

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['res.bank'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError("Bank's name must be unique!")
