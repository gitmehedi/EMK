from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import time,datetime


class DeliveryOrder(models.Model):
    _name = 'delivery.order'
    _description = 'Delivery Order'
    _inherit = ['mail.thread']
    _rec_name='name'
    _order = "approved_date desc"

    name = fields.Char(string='Name', index=True, readonly=True)
    so_date = fields.Datetime('Order Date', readonly=True, states={'draft': [('readonly', False)]})
    sequence_id = fields.Char('Sequence', readonly=True)
    deli_address = fields.Char('Delivery Address', readonly=True,states={'draft': [('readonly', False)]})
    sale_order_id = fields.Many2one('sale.order',string='Sale Order',required=True, readonly=True,states={'draft': [('readonly', False)]})
    parent_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade', readonly=True,related='sale_order_id.partner_id')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True,related='sale_order_id.payment_term_id')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True, states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('delivery.order.line', 'parent_id', string="Products", readonly=True,states={'draft': [('readonly', False)]})
    cash_ids = fields.One2many('cash.payment.line', 'pay_cash_id', string="Cash", readonly=True, invisible =True,states={'draft': [('readonly', False)]})
    cheque_ids=  fields.One2many('cheque.payment.line', 'pay_cash_id', string="Cheque", readonly=True,states={'draft': [('readonly', False)]})
    tt_ids = fields.One2many('tt.payment.line', 'pay_tt_id', string="T.T", readonly=True,states={'draft': [('readonly', False)]})
    lc_ids = fields.One2many('lc.payment.line', 'pay_lc_id', string="L/C", readonly=True,states={'draft': [('readonly', False)]})
    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True, default=lambda self: self.env.user)
    approver1_id = fields.Many2one('res.users', string="First Approval", readonly=True)
    approver2_id = fields.Many2one('res.users', string="Final Approval", readonly=True)
    requested_date = fields.Date(string="Requested Date", default=datetime.date.today(), readonly=True)
    approved_date = fields.Date(string='Final Approval Date',
                                states={'draft': [('invisible', True)],
                                        'validate': [('invisible', True)],
                                        'close': [('invisible', False), ('readonly', True)],
                                        'approve': [('invisible', False), ('readonly', True)]})
    confirmed_date = fields.Date(string="First Approval Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'), readonly=True)
    so_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sales Type', readonly=True,states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', "Submit"),
        ('validate', "Validate"),
        ('approve', "Second Approval"),
        ('close', "Approved")
    ], default='draft')

    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)

    #type_id = fields.Many2one('sale.order.type',string='Order Type')

    """ PI and LC """
    pi_no = fields.Many2one('proforma.invoice', string='PI Ref. No.')
    lc_no = fields.Many2one('letter.credit',string='LC Ref. No.')


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
    def action_draft(self):
        self.state = 'draft'
        self.line_ids.write({'state':'draft'})

    @api.multi
    def action_approve(self):
        if self.so_type == 'cash':
            self.payment_information_check()

            #check if payment is same as the subtotal amount
            self.check_cash_amount_with_subtotal()
            return self.create_delivery_order()

        elif self.so_type == 'lc_sales':
            #If LC and PI ref is present, go to the Final Approval
            if self.lc_no and self.pi_no:
                if self.lc_no.lc_value == self.products_price_sum() \
                        or self.lc_no.lc_value > self.products_price_sum():

                    return self.write({'state': 'close'})
                else:
                    raise UserError("LC Amount is not equal or greater than Product total price")
                    ## go to Second level approval

            # Has PI & no LC then go to second level approval
            if self.pi_no and not self.lc_no:
                ##Check 100MT checking for this product, company wise
                qty_sum = 0
                for line in self.line_ids:
                    product_pool = self.env['product.product'].search([('id','=',line.product_id.id),
                                                                        ('company_id','=',self.company_id.id),
                                                                        ('uom_id','=',line.uom_id.id)])

                    qty_sum = qty_sum + line.quantity

                    if qty_sum > product_pool.max_ordering_qty:
                        ## go to second level approval
                        raise ValidationError('%s : Max Ordering Qty. is over to 100 MT' %(line.product_id.display_name))
                        return self.write({'state': 'close'})

        self.state = 'approve'
        self.line_ids.write({'state': 'approve'})
        self.approver2_id = self.env.user

        self.create_delivery_order()

        return self.write({'state': 'approve', 'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')})


    def products_price_sum(self):
        product_line_subtotal = 0
        for do_product_line in self.line_ids:
            product_line_subtotal = product_line_subtotal + do_product_line.price_subtotal

    #@todo Need to refactor below method -- rabbi
    def check_cash_amount_with_subtotal(self):
        account_payment_pool = self.env['account.payment'].search(
            [('is_this_payment_checked', '=', False), ('sale_order_id', '=', self.sale_order_id.id),
             ('partner_id', '=', self.parent_id.id)])

        if not self.line_ids:
            return self.write({'state': 'approve'})  # Only Second level approval

        product_line_subtotal = 0
        for do_product_line in self.line_ids:
            product_line_subtotal = product_line_subtotal + do_product_line.price_subtotal

        cash_line_total_amount = 0
        for do_cash_line in self.cash_ids:
            cash_line_total_amount = cash_line_total_amount + do_cash_line.amount

        if not cash_line_total_amount or cash_line_total_amount == 0:
            account_payment_pool.write({'is_this_payment_checked': True})
            return self.write({'state': 'approve'})  # Only Second level approval

        if cash_line_total_amount >= product_line_subtotal:
            account_payment_pool.write({'is_this_payment_checked': True})
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


    def payment_information_check(self):
        for cash_line in self.cash_ids:

            if cash_line.account_payment_id.sale_order_id.id != self.sale_order_id.id:
                raise UserError("%s Payment Information is of a different Sale Order!" % (cash_line.account_payment_id.display_name))
                break;

            if cash_line.account_payment_id.is_this_payment_checked == True:
                raise UserError("Payment Information entered is already in use: %s" % (cash_line.account_payment_id.display_name))
                break;

    @api.one
    def action_validate(self):
        self.state = 'validate'
        self.line_ids.write({'state':'validate'})

    @api.one
    def action_close(self):
        self.state = 'close'
        self.line_ids.write({'state':'close'})
        self.approver1_id = self.env.user
        account_payment_pool = self.env['account.payment'].search(
            [('is_this_payment_checked', '=', False), ('sale_order_id', '=', self.sale_order_id.id),
             ('partner_id', '=', self.parent_id.id)])
        account_payment_pool.write({'is_this_payment_checked': True})

        return self.write({'state': 'close', 'confirmed_date': time.strftime('%Y-%m-%d %H:%M:%S')})


    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        self.set_products_info_automatically()

        account_payment_pool = self.env['account.payment'].search([('sale_order_id', '=', self.sale_order_id.id)])

        for payments in account_payment_pool:
            if payments.cheque_no:
                self.set_cheque_info_automatically(account_payment_pool)
                break;

            else:
                self.set_payment_info_automatically(account_payment_pool)



    def set_cheque_info_automatically(self, account_payment_pool):
        vals = []
        for payments in account_payment_pool:
            if payments.journal_id.id != 12:## Changeit! 12 == cash
                if not payments.is_this_payment_checked:
                    vals.append((0, 0, {'account_payment_id': payments.id,
                                        'amount': payments.amount,
                                        'bank': payments.deposited_bank,
                                        'branch': payments.bank_branch,
                                        'payment_date': payments.payment_date,
                                        'number':payments.cheque_no,
                                        }))

                self.cheque_ids = vals



    def set_products_info_automatically(self):
        if self.sale_order_id:
            val = []
            sale_order_obj = self.env['sale.order'].search([('id', '=', self.sale_order_id.id)])

            if sale_order_obj:
                self.warehouse_id = sale_order_obj.warehouse_id.id
                self.so_type = sale_order_obj.credit_sales_or_lc
                self.so_date = sale_order_obj.date_order
                self.deli_address = sale_order_obj.partner_shipping_id.name

                for record in sale_order_obj.order_line:
                    val.append((0, 0, {'product_id': record.product_id.id,
                                       'quantity': record.product_uom_qty,
                                       'pack_type': sale_order_obj.pack_type.id,
                                       'uom_id': record.product_uom.id,
                                       'commission_rate': record.commission_rate,
                                       'price_unit': record.price_unit,
                                       'price_subtotal': record.price_subtotal
                                       }))

            self.line_ids = val


    def set_payment_info_automatically(self, account_payment_pool):

        if account_payment_pool:
            vals = []
            for payments in account_payment_pool:
                if not payments.cheque_no:
                    if payments.sale_order_id and not payments.is_this_payment_checked:
                        vals.append((0, 0, {'account_payment_id': payments.id,
                                            'amount': payments.amount,
                                            'dep_bank':payments.deposited_bank,
                                            'branch':payments.bank_branch,
                                            'payment_date': payments.payment_date,
                                            }))

                        self.cash_ids = vals

    def action_process_unattached_payments(self):
        # account_payment_pool = self.env['account.payment'].search([('is_this_payment_checked', '=', False),
        #                                                            ('sale_order_id', '=', self.sale_order_id.id)])
        #
        # ## check if Payment Info is already tagged into DO Cash Line Tab!!
        # vals = []
        # if account_payment_pool:
        #     for payments in account_payment_pool:
        #         for cash_line in self.cash_ids:
        #             if cash_line.account_payment_id.id != payments.id:
        #                 vals.append((0, 0, {'account_payment_id': payments.id,
        #                                     'amount': payments.amount,
        #                                     'dep_bank': payments.deposited_bank,
        #                                     'branch': payments.bank_branch,
        #                                     'payment_date': payments.payment_date,
        #                                     }))
        #
        #
        #     self.cash_ids = vals
        pass
