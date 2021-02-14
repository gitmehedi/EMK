from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import time, datetime


class DeliveryAuthorization(models.Model):
    _name = 'delivery.authorization'
    _description = 'Delivery Authorization'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _order = "id desc"

    name = fields.Char(string='Delivery Authorization', index=True, readonly=True, default="/")

    def _get_sale_order_currency(self):
        self.currency_id = self.sale_order_id.currency_id

    currency_id = fields.Many2one('res.currency', string='Currency', compute='_get_sale_order_currency', readonly=True)

    so_date = fields.Datetime('Order Date', readonly=True)
    sequence_id = fields.Char('Sequence', readonly=True)
    deli_address = fields.Char('Delivery Address', readonly=True)

    parent_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade', readonly=True,
                                related='sale_order_id.partner_id', track_visibility='onchange')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True,
                                      related='sale_order_id.payment_term_id')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True,
                                   states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('delivery.authorization.line', 'parent_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]})
    cash_ids = fields.One2many('cash.payment.line', 'pay_cash_id', string="Cash", readonly=True, invisible=True,
                               states={'draft': [('readonly', False)]})
    cheque_ids = fields.One2many('cheque.payment.line', 'pay_cash_id', string="Cheque", readonly=True,
                                 states={'draft': [('readonly', False)]})

    cheque_rcv_all_ids = fields.One2many('cheque.entry.line', 'pay_all_cq_id', string="Cheque Received", readonly=True,
                                         states={'draft': [('readonly', False)]})

    tt_ids = fields.One2many('tt.payment.line', 'pay_tt_id', string="T.T", readonly=True,
                             states={'draft': [('readonly', False)]})
    lc_ids = fields.One2many('lc.payment.line', 'pay_lc_id', string="L/C", readonly=True,
                             states={'draft': [('readonly', False)]})
    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True,
                                   default=lambda self: self.env.user)
    approver1_id = fields.Many2one('res.users', string="Final Approval", readonly=True)
    approver2_id = fields.Many2one('res.users', string="First Approval", readonly=True)
    requested_date = fields.Date(string="Requested Date", default=datetime.date.today(), readonly=True)
    approved_date = fields.Date(string='Final Approval Date',
                                states={'draft': [('invisible', True)],
                                        'validate': [('invisible', True)],
                                        'close': [('invisible', False), ('readonly', True)],
                                        'approve': [('invisible', False), ('readonly', True)]})
    confirmed_date = fields.Date(string="Approval Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'), readonly=True,
                                 track_visibility='onchange')

    so_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
        ('tt_sales', 'TT'),
        ('contract_sales', 'Sales Contract'),
    ], string='Sales Type', readonly=True, track_visibility='onchange')

    state = fields.Selection([
        ('draft', "Submit"),
        ('validate', "Validate"),
        ('approve', "Second Approval"),
        ('close', "Approved"),
        ('refused', 'Refused'),
    ], default='draft', track_visibility='onchange')

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', readonly=True,
                                        track_visibility='onchange')

    @api.multi
    @api.depends('sale_order_id.procurement_group_id')
    def _compute_picking_ids(self):
        for order in self.sale_order_id:
            order.picking_ids = self.env['stock.picking'].search(
                [('group_id', '=', order.procurement_group_id.id)]) if order.procurement_group_id else []
            self.delivery_count = len(order.picking_ids)

    """ PI and LC """
    pi_id = fields.Many2one('proforma.invoice', string='PI Ref. No.', compute="_calculate_pi_id", store=False,
                            track_visibility='onchange')
    lc_id = fields.Many2one('letter.credit', string='LC Ref. No.', compute="_calculate_lc_id", store=False,
                            track_visibility='onchange')

    @api.multi
    def _calculate_pi_id(self):
        for p in self:
            p.pi_id = p.sale_order_id.pi_id.id

    @api.multi
    def _calculate_lc_id(self):
        for da_lc in self:
            da_lc.lc_id = da_lc.sale_order_id.lc_id.id

    """ Payment information"""
    amount_untaxed = fields.Float(string='Ordered Amount', compute='_compute_amount_untaxed',
                                  track_visibility='onchange')


    @api.depends('line_ids.delivery_qty')
    def _compute_amount_untaxed(self):
        for rec in self:
            for line in rec.line_ids:
                rec.amount_untaxed = line.price_unit * line.delivery_qty
                rec.line_ids.price_subtotal = line.price_unit * line.delivery_qty


    tax_value = fields.Float(string='Taxes', readonly=True)
    total_amount = fields.Float(string='Total', readonly=True, track_visibility='onchange')
    total_payment_received = fields.Float(string='Payment Received', readonly=True, track_visibility='onchange')
    total_cheque_rcv_amount_not_honored = fields.Float(string='Cheque Received', readonly=True,
                                                       track_visibility='onchange')

    sale_order_id = fields.Many2one('sale.order',
                                    string='Sale Order',
                                    readonly=True,
                                    domain=[('da_btn_show_hide', '=', False), ('state', '=', 'done')],
                                    track_visibility='onchange')

    @api.multi
    def _compute_do_button_visibility(self):

        for da in self:
            delivery_order_pool = da.env['delivery.order'].search([('delivery_order_id', '=', da.id)])
            if delivery_order_pool:
                da.delivery_order_btn_hide = True
            else:
                da.delivery_order_btn_hide = False

    delivery_order_btn_hide = fields.Boolean(string='Is DO Button Visible', store=False,
                                             compute='_compute_do_button_visibility')

    """ All functions """

    @api.model
    def create(self, vals):

        if 'sale_order_id' in vals:
            ou = self.env['sale.order'].search([('id', '=', vals['sale_order_id'])]).operating_unit_id
            seq = self.env['ir.sequence'].next_by_code_new('delivery.authorization', self.requested_date, ou) or '/'
            vals['name'] = seq

        return super(DeliveryAuthorization, self).create(vals)

    @api.multi
    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise UserError('You can not delete record which is in Approved state')
            order.line_ids.unlink()
        return super(DeliveryAuthorization, self).unlink()

    @api.one
    def action_refuse(self):
        self.state = 'refused'

    @api.one
    def action_draft(self):
        self.state = 'draft'

    """ Action for Validate Button"""

    @api.one
    def action_approve(self):
        self.state = 'validate'
        self.approver2_id = self.env.user
        self.approved_date = time.strftime('%Y-%m-%d %H:%M:%S')

    """ Action for Approve Button"""

    @api.multi
    def action_close(self):

        self.approver1_id = self.env.user

        # Automatically Create Delivery Order
        self._create_delivery_authorization_back_order()
        self._automatic_delivery_order_creation()

        return self.write({'state': 'close', 'confirmed_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    """ Action for Confirm button"""



    @api.multi
    def _automatic_delivery_order_creation(self):
        # System confirms that one Sale Order will have only one DA & DO, so check with Sales Order ID
        do_sale_pool = self.env['delivery.order'].search([('sale_order_id', '=', self.sale_order_id.id)])
        #if not do_sale_pool:
        vals = {
            'delivery_order_id': self.id,
            'sale_order_id': self.sale_order_id.id,
            'deli_address': self.sale_order_id.partner_shipping_id.name,
            'currency_id': self.sale_order_id.type_id.currency_id,
            'parent_id': self.sale_order_id.partner_id,
            'so_type': self.sale_order_id.credit_sales_or_lc,
            'so_date': self.sale_order_id.date_order,
            'state': 'approved',
            'operating_unit_id': self.operating_unit_id.id
        }

        do_pool = self.env['delivery.order'].create(vals)

        for record in self.line_ids:
            qty = 0
            if record.delivery_qty < record.quantity:
                qty = record.delivery_qty
            else:
                qty = record.quantity

            da_line = {
                'parent_id': do_pool.id,
                'product_id': record.product_id.id,
                'quantity': qty,
                'delivery_qty': record.delivery_qty,
                'pack_type': self.sale_order_id.pack_type.id,
                'uom_id': record.uom_id.id,
            }

            self.env['delivery.order.line'].create(da_line)

        # generate stock picking for a DO
        do_pool.create_delivery_order()
        do_pool.action_view_delivery()

        # unreserve the reserve qty of stock pickings
        if self.sale_order_id:
            picking_to_unreserve = self.sale_order_id.picking_ids.filtered(
                lambda x: x.quant_reserved_exist and (x.state in ['draft', 'partially_available', 'assigned']))
            if picking_to_unreserve:
                picking_to_unreserve.do_unreserve()

    # -----------------------
    # DA Back Order
    # -----------------------
    def _create_delivery_authorization_back_order(self):
        daa_pool = self.search([('sale_order_id','=',self.sale_order_id.id)])


        if self.line_ids.delivery_qty < self.line_ids.quantity:

            vals2 = {
                'sale_order_id': self.sale_order_id.id,
                'deli_address': self.sale_order_id.partner_shipping_id.name,
                'currency_id': self.sale_order_id.type_id.currency_id,
                'parent_id': self.sale_order_id.partner_id,
                'so_type': self.sale_order_id.credit_sales_or_lc,
                'so_date': self.sale_order_id.date_order,
                'amount_untaxed': self.sale_order_id.amount_total,
                'tax_value': self.sale_order_id.amount_tax,
                'total_amount': self.sale_order_id.amount_total,
                'operating_unit_id': self.operating_unit_id.id,
                'state': 'draft',
            }

            # Update DA Qty
            self.line_ids.write({'quantity': self.line_ids.delivery_qty})

            da_pool = self.env['delivery.authorization'].create(vals2)

            sum_delivery_qty = 0

            for d in daa_pool:
                for d_line in d.line_ids:
                    sum_delivery_qty += d_line.delivery_qty


            for recs in self.line_ids:

                da_line2 = {
                    'parent_id': da_pool.id,
                    'product_id': recs.product_id.id,
                    'quantity': self.sale_order_id.order_line.product_uom_qty - sum_delivery_qty,
                    'pack_type': self.sale_order_id.pack_type.id,
                    'uom_id': recs.uom_id.id,
                    'price_unit': recs.price_unit,
                    'commission_rate': recs.commission_rate,
                    'price_subtotal': recs.price_subtotal,
                    'tax_id': recs.tax_id.id,
                    'delivery_qty': self.sale_order_id.order_line.product_uom_qty - sum_delivery_qty,
                    'sale_order_id': self.sale_order_id.id,
                }

                self.env['delivery.authorization.line'].create(da_line2)



    @api.multi
    def action_view_delivery_order(self):
        form_view = self.env.ref('delivery_order.delivery_order_layer_form')
        action = self.env.ref('delivery_order.delivery_order_layer_action').read()[0]
        do_pool = self.env['delivery.order'].search([('sale_order_id', '=', self.sale_order_id.id)])

        if len(do_pool) > 1:
            action['domain'] = [('id', 'in', do_pool.ids)]
        elif do_pool:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = do_pool.id
        return action


    @api.multi
    def action_validate(self):
        if self.so_type == 'cash' or self.so_type == 'tt_sales':
            cash_check = self.payments_amount_checking_with_products_subtotal()
            #self._create_delivery_authorization_back_order()
            return cash_check

        elif self.so_type == 'lc_sales' or self.so_type == 'contract_sales':
            if self.lc_id and self.pi_id:
                if self.lc_id.lc_value >= self.total_sub_total_amount():

                    self._create_delivery_authorization_back_order()
                    self._automatic_delivery_order_creation()

                    self.write({'state': 'close'})  # Final Approval
                else:
                    self.write({'state': 'approve'})  # Second approval

            elif self.pi_id and not self.lc_id:
                res = {}
                list = dict.fromkeys(set([val.product_id.product_tmpl_id.id for val in self.line_ids]), 0)
                for line in self.line_ids:
                    list[line.product_id.product_tmpl_id.id] = list[line.product_id.product_tmpl_id.id] + line.delivery_qty

                for rec in list:
                    ordered_qty_pool = self.env['ordered.qty'].search([('lc_id', '=', False),
                                                                       ('company_id', '=', self.company_id.id),
                                                                       ('product_id', '=', rec)])

                    res['product_id'] = rec
                    res['ordered_qty'] = list[rec]
                    res['delivery_auth_no'] = self.id

                    if not ordered_qty_pool:
                        res['available_qty'] = 100 - list[rec]
                        if list[rec] > 100:
                            res['available_qty'] = 0

                        self.env['ordered.qty'].create(res)

                        self._create_delivery_authorization_back_order()
                        self._automatic_delivery_order_creation()
                        self.write({'state': 'close'})  # Final Approval
                    # else:
                    #     avail_qty_sum = 0
                    #
                    #     for orders in ordered_qty_pool:
                    #         avail_qty_sum += orders.available_qty
                    #
                    #     if list[rec] > avail_qty_sum:
                    #         res['available_qty'] = 0
                    #         self.env['ordered.qty'].create(res)
                    #         # self.write({'state': 'close'})  # Final Approval
                    #     else:
                    #         res['available_qty'] = avail_qty_sum - list[rec]
                    #         if res['available_qty'] > 100:
                    #             res['available_qty'] = 0
                    #
                    #     self._create_delivery_authorization_back_order()
                    #     self._automatic_delivery_order_creation()
                    #     self.write({'state': 'close'})  # Final Approval
                    #     self.env['ordered.qty'].create(res)
                    #
                    # if list[rec] > 100 or res['available_qty'] == 0:
                        # product_pool = self.env['product.template'].search([('id', '=', rec)])
                    wizard_form = self.env.ref('delivery_order.max_do_without_lc_view', False)
                    view_id = self.env['max.delivery.without.lc.wizard']

                    return {
                        'name': _('Max Ordering Confirm'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'max.delivery.without.lc.wizard',
                        'res_id': view_id.id,
                        'view_id': wizard_form.id,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {'delivery_order_id': self.id, 'product_name': line.product_id.display_name}
                    }
            else:
                self.state = 'approve'  # second

        elif self.so_type == 'credit_sales':
            self._create_delivery_authorization_back_order()
            self._automatic_delivery_order_creation()
            self.state = 'close'

    def total_sub_total_amount(self):
        total_amt = 0
        for orders in self:
            for do_line in orders.line_ids:
                total_amt = total_amt + do_line.price_subtotal

        return total_amt

    @api.multi
    def payments_amount_checking_with_products_subtotal(self):
        if not self.line_ids:
            return self.write({'state': 'validate'})  # Only Second level approval

        if not self.total_payment_received or self.total_payment_received == 0:
            return self.write({'state': 'validate'})  # Only Second level approval

        if self.total_payment_received >= self.total_amount:
            self._create_delivery_authorization_back_order()
            self._automatic_delivery_order_creation()
            return self.write({'state': 'close'})  # directly go to final approval level
        else:
            return self.write({'state': 'validate'})  # Only Second level approval

    def create_delivery_order(self):
        for order in self.sale_order_id:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.sale_order_id.force_quotation_send()

            order.order_line._action_procurement_create()

        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.sale_order_id.action_done()
        return True

    def action_process_unattached_payments(self):
        self.process_cheque_payment()
        self.process_cash_payment()
        self.process_all_cheque_received_entry()

        # process total payment received amount
        self.process_total_payment_received_amount()

    # Process all the entered Cheque Received entry
    def process_all_cheque_received_entry(self):
        if self.cheque_rcv_all_ids:
            self.cheque_rcv_all_ids.unlink()

        for pay in self:
            cheque_rcv_pool = pay.env['accounting.cheque.received'].search(
                [('partner_id', '=', pay.sale_order_id.partner_id.id), ('state', '!=', 'honoured'),
                 ('sale_order_id', '=', pay.sale_order_id.id)])

            val_bank = []
            for bank_line in self.cheque_rcv_all_ids:
                val_bank.append(bank_line.cheque_info_id)

            vals = []

            for payments in cheque_rcv_pool:

                if payments.id not in val_bank:
                    c = 0
                    if payments.currency_id:
                        if payments.currency_id != self.currency_id:
                            if self.currency_id.rate == 1:
                                c = payments.cheque_amount / payments.currency_id.rate
                            else:
                                c = self.currency_id.rate * payments.cheque_amount
                        else:
                            c = payments.cheque_amount

                    # if payments.journal_id.currency_id:
                    #     currency = payments.journal_id.currency_id.id
                    # else:
                    #     currency = payments.company_id.currency_id.id

                    vals.append((0, 0, {'cheque_info_id': payments.id,
                                        'amount': payments.cheque_amount,
                                        'bank': payments.bank_name.name,
                                        'branch': payments.branch_name,
                                        'payment_date': payments.payment_date,
                                        'number': payments.cheque_no,
                                        'currency_id': payments.currency_id.id,
                                        'state': payments.state,
                                        'converted_amount': c,
                                        }))

            pay.cheque_rcv_all_ids = vals

            ## Sum of cheques amount
            cheque_line_total_amount = 0
            converted_amount = 0

            for do_cheque_line in pay.cheque_rcv_all_ids:
                cheque_line_total_amount = cheque_line_total_amount + do_cheque_line.converted_amount

                # converted_amount = cheque_line_total_amount
                # if do_cheque_line.currency_id != self.currency_id:
                #     converted_amount = cheque_line_total_amount * self.currency_id.rate
                # else:
                #     converted_amount = cheque_line_total_amount

            pay.total_cheque_rcv_amount_not_honored = cheque_line_total_amount

    def process_total_payment_received_amount(self):
        # Sum of cash amount
        cash_line_total_amount = 0
        for do_cash_line in self.cash_ids:
            cash_line_total_amount = cash_line_total_amount + do_cash_line.amount

        ## Sum of cheques amount
        cheque_line_total_amount = 0
        for do_cheque_line in self.cheque_ids:
            cheque_line_total_amount = cheque_line_total_amount + do_cheque_line.amount

        total_rcv = cash_line_total_amount + cheque_line_total_amount

        # Convert Toal Payment Received to Sale Order Currency
        self.total_payment_received = total_rcv * self.currency_id.rate

    def process_cash_payment(self):
        if self.cash_ids:
            self.cash_ids.unlink()

        account_payment_pool = self.env['account.payment'].search(
            [('state', '!=', 'draft'), ('sale_order_id', '=', self.sale_order_id.id)])

        for acc in account_payment_pool:

            acc_move_line_cash = self.env['account.move.line'].search(
                [('credit', '=', 0.00), ('payment_id', '=', acc.id)])

            vals_bank = []

            for bank_payments in acc_move_line_cash:
                vals_bank.append((0, 0, {'id': bank_payments.id,
                                         'amount': bank_payments.debit,
                                         'dep_bank': acc.deposited_bank,
                                         'branch': acc.bank_branch,
                                         'payment_date': bank_payments.date,
                                         'amount_currency': bank_payments.currency_id.id,
                                         'amount_in_diff_currency': bank_payments.amount_currency,
                                         'currency_id': bank_payments.move_id.currency_id.id,
                                         'account_payment_id': bank_payments.name
                                         }))

            self.cash_ids = vals_bank

    @api.multi
    def process_cheque_payment(self):
        if self.cheque_ids:
            self.cheque_ids.unlink()

        for pay in self:
            cheque_rcv_pool = pay.env['accounting.cheque.received'].search(
                [('partner_id', '=', pay.sale_order_id.partner_id.id), ('state', '=', 'honoured'),
                 ('sale_order_id', '=', pay.sale_order_id.id)])

            for cq_obj in cheque_rcv_pool:
                acc_move_line_cheque = pay.env['account.move.line'].search(
                    [('cheque_received_id', '=', cq_obj.id), ('credit', '=', 0.00)])

                vals = []

                for payments in acc_move_line_cheque:
                    # if not cq_obj.is_this_payment_checked:
                    vals.append((0, 0, {'id': payments.id,
                                        'amount': payments.debit,
                                        'bank': cq_obj.bank_name.name,
                                        'branch': cq_obj.branch_name,
                                        'payment_date': cq_obj.payment_date,
                                        'number': cq_obj.cheque_no,
                                        'label': payments.name,
                                        'amount_currency': payments.currency_id.id,
                                        'amount_in_diff_currency': payments.amount_currency,
                                        'currency_id': payments.move_id.currency_id.id,
                                        }))

                pay.cheque_ids = vals

    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        # if users_obj.has_group('gbs_application_group.group_cxo'):
        #     domain = [
        #         ('state', 'in', ['validate'])]
        #     return domain
        if users_obj.has_group('gbs_application_group.group_head_account'):
            domain = [
                ('state', 'in', ['validate'])]
            return domain
        elif users_obj.has_group('account.group_account_user'):
            domain = [
                ('state', 'in', ['draft'])]
            return domain
        else:
            return False

    ################
    # 100 MT Logic
    ###############
    @api.multi
    def update_lc_id_for_houndred_mt(self):
        for delivery in self:
            ordered_qty_pool = delivery.env['ordered.qty'].search([('delivery_auth_no', '=', delivery.id)])
            if ordered_qty_pool:
                ordered_qty_pool.write({'lc_id': delivery.lc_id.id})

            ## Update LC No to Stock Picking Obj
            stock_picking_id = delivery.sale_order_id.picking_ids
            stock_picking_id.write({'lc_id': delivery.lc_id.id})



class OrderedQty(models.Model):
    _name = 'ordered.qty'
    _description = 'Store Product wise ordered qty to track max qty value'

    product_id = fields.Many2one('product.template', string='Product')
    ordered_qty = fields.Float(string='Ordered Qty')
    available_qty = fields.Float(string='Allowed Qty', default=0.00)  ## available_qty = max_qty - ordered_qty
    lc_id = fields.Many2one('letter.credit', string='LC No')
    delivery_auth_no = fields.Many2one('delivery.authorization', string='Delivery Authrozation ref')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'product_sales_pricelist'))
