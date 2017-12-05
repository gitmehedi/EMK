from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import time, datetime


class DeliveryOrder(models.Model):
    _name = 'delivery.order'
    _description = 'Delivery Order'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = "approved_date desc,name desc"

    name = fields.Char(string='Name', index=True, readonly=True)

    so_date = fields.Datetime('Order Date', readonly=True, states={'draft': [('readonly', False)]})
    sequence_id = fields.Char('Sequence', readonly=True)
    deli_address = fields.Char('Delivery Address', readonly=True, states={'draft': [('readonly', False)]})

    parent_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade', readonly=True,
                                related='sale_order_id.partner_id')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True,
                                      related='sale_order_id.payment_term_id')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True,
                                   states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('delivery.order.line', 'parent_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]})
    cash_ids = fields.One2many('cash.payment.line', 'pay_cash_id', string="Cash", readonly=True, invisible=True,
                               states={'draft': [('readonly', False)]})
    cheque_ids = fields.One2many('cheque.payment.line', 'pay_cash_id', string="Cheque", readonly=True,
                                 states={'draft': [('readonly', False)]})
    tt_ids = fields.One2many('tt.payment.line', 'pay_tt_id', string="T.T", readonly=True,
                             states={'draft': [('readonly', False)]})
    lc_ids = fields.One2many('lc.payment.line', 'pay_lc_id', string="L/C", readonly=True,
                             states={'draft': [('readonly', False)]})
    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True,
                                   default=lambda self: self.env.user)
    approver1_id = fields.Many2one('res.users', string="First Approval", readonly=True)
    approver2_id = fields.Many2one('res.users', string="Final Approval", readonly=True)
    requested_date = fields.Date(string="Requested Date", default=datetime.date.today(), readonly=True)
    approved_date = fields.Date(string='Approval Date',
                                states={'draft': [('invisible', True)],
                                        'validate': [('invisible', True)],
                                        'close': [('invisible', False), ('readonly', True)],
                                        'approve': [('invisible', False), ('readonly', True)]})
    confirmed_date = fields.Date(string="Approval Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'), readonly=True)
    so_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sales Type', readonly=True, states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', "Submit"),
        ('validate', "Validate"),
        ('approve', "Second Approval"),
        ('close', "Approved"),
        ('refused', 'Refused'),
    ], default='draft')

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')

    @api.multi
    @api.depends('sale_order_id.procurement_group_id')
    def _compute_picking_ids(self):
        for order in self.sale_order_id:
            order.picking_ids = self.env['stock.picking'].search(
                [('group_id', '=', order.procurement_group_id.id)]) if order.procurement_group_id else []
            self.delivery_count = len(order.picking_ids)

    """ PI and LC """
    pi_no = fields.Many2one('proforma.invoice', string='PI Ref. No.', readonly=True,
                            states={'draft': [('readonly', False)]})
    lc_no = fields.Many2one('letter.credit', string='LC Ref. No.', readonly=True,
                            states={'draft': [('readonly', False)]})

    """ Payment information"""
    amount_untaxed = fields.Float(string='Untaxed Amount', readonly=True)
    tax_value = fields.Float(string='Taxes', readonly=True)
    total_amount = fields.Float(string='Total', readonly=True)

    sale_order_id = fields.Many2one('sale.order',
                                    string='Sale Order',
                                    readonly=True,
                                    domain=[('da_btn_show_hide', '=', False), ('state', '=', 'done')],
                                    states={'draft': [('readonly', False)]})

    """ All functions """

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('delivery.order') or '/'
        vals['name'] = seq
        return super(DeliveryOrder, self).create(vals)

    @api.multi
    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise UserError('You can not delete this.')
            order.line_ids.unlink()
        return super(DeliveryOrder, self).unlink()

    @api.one
    def action_refuse(self):
        self.state = 'refused'
        # self.line_ids.write({'state': 'close'})

    @api.one
    def action_draft(self):
        self.state = 'draft'

    """ DO button box action """

    @api.multi
    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.sale_order_id.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action

    """ Action for Validate Button"""

    @api.one
    def action_approve(self):
        self.state = 'validate'

    """ Action for Approve Button"""

    @api.one
    def action_close(self):

        self.approver1_id = self.env.user
        account_payment_pool = self.env['account.payment'].search(
            [('is_this_payment_checked', '=', False), ('sale_order_id', '=', self.sale_order_id.id),
             ('partner_id', '=', self.parent_id.id)])
        account_payment_pool.write({'is_this_payment_checked': True})

        self.create_delivery_order()
        self.update_sale_order_da_qty()
        return self.write({'state': 'close', 'confirmed_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    """ Action for Confirm button"""

    @api.multi
    def action_validate(self):

        if self.so_type == 'cash':
            self.payment_information_check()
            cash_check = self.payments_amount_checking_with_products_subtotal()
            return cash_check

        elif self.so_type == 'lc_sales':

            if self.pi_no:
                pi_pool = self.env['proforma.invoice'].search([('sale_order_id', '=', self.sale_order_id.id)])
                if not pi_pool:
                    raise UserError('PI is of a different Sale Order')

            if self.lc_no and self.pi_no:
                if self.lc_no.lc_value >= self.total_sub_total_amount():
                    self.create_delivery_order()
                    self.update_sale_order_da_qty()
                    self.write({'state': 'close'})  # Final Approval
                else:
                    self.write({'state': 'approve'})  # Second approval

            elif self.pi_no and not self.lc_no:
                res = {}
                list = dict.fromkeys(set([val.product_id.product_tmpl_id.id for val in self.line_ids]), 0)
                for line in self.line_ids:
                    list[line.product_id.product_tmpl_id.id] = list[line.product_id.product_tmpl_id.id] + line.quantity

                for rec in list:
                    ordered_qty_pool = self.env['ordered.qty'].search([('lc_no', '=', False),
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
                    else:
                        for orders in ordered_qty_pool:
                            if not orders.lc_no:
                                if list[rec] > orders.available_qty:
                                    res['available_qty'] = 0
                                    orders.create(res)
                                else:
                                    res['available_qty'] = orders.available_qty - list[rec]
                                    if res['available_qty'] > 100:
                                        res['available_qty'] = 0

                                    self.create_delivery_order()
                                    self.update_sale_order_da_qty()

                                    self.write({'state': 'close'})  # Final Approval
                                    orders.create(res)

                    if list[rec] > 100:
                        wizard_form = self.env.ref('delivery_order.error_exception_wizard_view', False)
                        view_id = self.env['error.exception.wizard']

                        return {
                            'name': _('Confirmation Pop Up'),
                            'type': 'ir.actions.act_window',
                            'res_model': 'error.exception.wizard',
                            'res_id': view_id.id,
                            'view_id': wizard_form.id,
                            'view_type': 'form',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': {'delivery_order_id': self.id}
                        }
            else:
                self.state = 'approve'  # second

        elif self.so_type == 'credit_sales':
            self.create_delivery_order()
            self.update_sale_order_da_qty()
            self.state = 'close'

    def total_sub_total_amount(self):
        total_amt = 0
        for orders in self:
            for do_line in orders.line_ids:
                total_amt = total_amt + do_line.price_subtotal

        return total_amt

    @api.one
    def action_wizard_custom_user_msg_lc(self):

        res1 = self.env.ref('delivery_order.view_max_order_qty_wizard')
        return {
            'name': ('Custom Message to User'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res1 and res1.id or False,
            'res_model': 'max.order.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',

        }

    @api.one
    def payments_amount_checking_with_products_subtotal(self):

        account_payment_pool = self.env['account.payment'].search(
            [('is_this_payment_checked', '=', False), ('sale_order_id', '=', self.sale_order_id.id),
             ('partner_id', '=', self.parent_id.id)])

        if not self.line_ids:
            return self.write({'state': 'approve'})  # Only Second level approval

        ## Sum of cash amount
        cash_line_total_amount = 0
        for do_cash_line in self.cash_ids:
            cash_line_total_amount = cash_line_total_amount + do_cash_line.amount

        ## Sum of cheques amount
        cheque_line_total_amount = 0
        for do_cheque_line in self.cheque_ids:
            cheque_line_total_amount = cheque_line_total_amount + do_cheque_line.amount

        total_cash_cheque_amount = cash_line_total_amount + cheque_line_total_amount

        if not total_cash_cheque_amount or total_cash_cheque_amount == 0:
            account_payment_pool.write({'is_this_payment_checked': True})
            return self.write({'state': 'approve'})  # Only Second level approval

        if total_cash_cheque_amount >= self.total_amount:
            account_payment_pool.write({'is_this_payment_checked': True})
            self.create_delivery_order()
            self.update_sale_order_da_qty()
            return self.write({'state': 'close'})  # directly go to final approval level
        else:
            account_payment_pool.write({'is_this_payment_checked': True})
            return self.write({'state': 'approve'})  # Only Second level approval

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

    @api.one
    def payment_information_check(self):
        for cash_line in self.cash_ids:

            if cash_line.account_payment_id.sale_order_id.id != self.sale_order_id.id:
                raise UserError("%s Payment Information is of a different Sale Order!" % (
                    cash_line.account_payment_id.display_name))
                break;

            if cash_line.account_payment_id.is_this_payment_checked == True:
                raise UserError(
                    "Payment Information entered is already in use: %s" % (cash_line.account_payment_id.display_name))
                break;

    def update_sale_order_da_qty(self):
        for da_line in self.line_ids:
            for sale_line in self.sale_order_id.order_line:
                if da_line.product_id.id == sale_line.product_id.id:
                    vals = sale_line.da_qty - da_line.quantity
                    sale_line.write({'da_qty': vals})

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.line_ids.quantity < 0 or self.line_ids.quantity == 0.00:
            raise UserError("Qty can not be Zero or Negative value")

    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        self.set_products_info_automatically()

        account_payment_pool = self.env['account.payment'].search([('sale_order_id', '=', self.sale_order_id.id)])

        for payments in account_payment_pool:
            if payments.journal_id.type == 'bank':
                self.set_cheque_info_automatically(account_payment_pool)
            elif payments.journal_id.type == 'cash':
                self.set_payment_info_automatically(account_payment_pool)

    @api.one
    def set_cheque_info_automatically(self, account_payment_pool):
        vals = []
        for payments in account_payment_pool:
            if payments.journal_id.type != 'cash':
                if not payments.is_this_payment_checked:
                    vals.append((0, 0, {'account_payment_id': payments.id,
                                        'amount': payments.amount,
                                        'bank': payments.deposited_bank,
                                        'branch': payments.bank_branch,
                                        'payment_date': payments.payment_date,
                                        'number': payments.cheque_no,
                                        }))

                self.cheque_ids = vals

    @api.one
    def set_payment_info_automatically(self, account_payment_pool):

        if account_payment_pool:
            vals = []
            for payments in account_payment_pool:
                if payments.journal_id.type == 'cash':
                    if payments.sale_order_id and not payments.is_this_payment_checked:
                        vals.append((0, 0, {'account_payment_id': payments.id,
                                            'amount': payments.amount,
                                            'dep_bank': payments.deposited_bank,
                                            'branch': payments.bank_branch,
                                            'payment_date': payments.payment_date,
                                            }))

                        self.cash_ids = vals

    @api.one
    def set_products_info_automatically(self):
        if self.sale_order_id:
            val = []
            sale_order_obj = self.env['sale.order'].search([('id', '=', self.sale_order_id.id)])

            if sale_order_obj:
                self.warehouse_id = sale_order_obj.warehouse_id.id
                self.so_type = sale_order_obj.credit_sales_or_lc
                self.so_date = sale_order_obj.date_order
                self.deli_address = sale_order_obj.partner_shipping_id.name
                self.pi_no = sale_order_obj.pi_no.id
                self.lc_no = sale_order_obj.lc_no.id

                for record in sale_order_obj.order_line:
                    val.append((0, 0, {'product_id': record.product_id.id,
                                       'quantity': record.product_uom_qty,
                                       'pack_type': sale_order_obj.pack_type.id,
                                       'uom_id': record.product_uom.id,
                                       'commission_rate': record.commission_rate,
                                       'price_unit': record.price_unit,
                                       'price_subtotal': record.price_subtotal,
                                       'tax_id': record.tax_id.id
                                       }))
                self.amount_untaxed = sale_order_obj.amount_untaxed
                self.tax_value = sale_order_obj.amount_tax
                self.total_amount = sale_order_obj.amount_total

            self.line_ids = val

    def action_process_unattached_payments(self):
        account_payment_pool = self.env['account.payment'].search(
            [('is_this_payment_checked', '=', False), ('sale_order_id', '=', self.sale_order_id.id)])

        for acc in account_payment_pool:
            if acc.journal_id.type == 'cash':
                val = []
                for cash_line in self.cash_ids:
                    val.append(cash_line.account_payment_id.id)

                vals = []
                for payments in acc:
                    if payments.id not in val:
                        vals.append((0, 0, {'account_payment_id': payments.id,
                                            'amount': payments.amount,
                                            'dep_bank': payments.deposited_bank,
                                            'branch': payments.bank_branch,
                                            'payment_date': payments.payment_date,
                                            }))

                self.cash_ids = vals

            elif acc.journal_id.type == 'bank':
                val_bank = []
                for bank_line in self.cheque_ids:
                    val_bank.append(bank_line.account_payment_id.id)

                vals_bank = []

                for bank_payments in acc:
                    if bank_payments.id not in val_bank:
                        vals_bank.append((0, 0, {'account_payment_id': bank_payments.id,
                                                 'amount': bank_payments.amount,
                                                 'bank': bank_payments.deposited_bank,
                                                 'branch': bank_payments.bank_branch,
                                                 'payment_date': bank_payments.payment_date,
                                                 }))

                self.cheque_ids = vals_bank


class OrderedQty(models.Model):
    _name = 'ordered.qty'
    _description = 'Store Product wise ordered qty to track max qty value'
    # _order = "delivery_auth_no,desc"

    product_id = fields.Many2one('product.template', string='Product')
    ordered_qty = fields.Float(string='Ordered Qty')
    available_qty = fields.Float(string='Allowed Qty', default=0.00)  ## available_qty = max_qty - ordered_qty
    lc_no = fields.Many2one('letter.credit', string='LC No')
    delivery_auth_no = fields.Many2one('delivery.order', string='Delivery Authrozation ref')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'product_sales_pricelist'))
