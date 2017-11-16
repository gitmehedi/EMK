from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning
import time,datetime


class DeliveryOrder(models.Model):
    _name = 'delivery.order'
    _description = 'Delivery Order'
    _inherit = ['mail.thread']
    _rec_name='name'
    _order = "approved_date desc,name desc"


    name = fields.Char(string='Name', index=True, readonly=True)

    so_date = fields.Datetime('Order Date', readonly=True, states={'draft': [('readonly', False)]})
    sequence_id = fields.Char('Sequence', readonly=True)
    deli_address = fields.Char('Delivery Address', readonly=True,states={'draft': [('readonly', False)]})

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
    ], string='Sales Type', readonly=True,states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', "Submit"),
        ('validate', "Validate"),
        ('approve', "Second Approval"),
        ('close', "Approved")
    ], default='draft')

    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)

    """ PI and LC """
    pi_no = fields.Many2one('proforma.invoice', string='PI Ref. No.', readonly=True, states={'draft': [('readonly', False)]})
    lc_no = fields.Many2one('letter.credit',string='LC Ref. No.', readonly=True, states={'draft': [('readonly', False)]})

    """ Payment information"""
    amount_untaxed = fields.Float(string='Untaxed Amount', readonly=True)
    tax_value = fields.Float(string='Taxes',readonly=True)
    total_amount = fields.Float(string='Total',readonly=True)

    sale_order_id = fields.Many2one('sale.order',
                                    string='Sale Order',
                                    required=True,readonly=True,
                                    domain=[('da_btn_show_hide','=',True)],
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
    def action_draft(self):
        self.state = 'close'
        self.line_ids.write({'state':'close'})

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
    @api.one
    def action_validate(self):
        if self.so_type == 'cash':
            self.payment_information_check()
            cash_check = self.check_cash_amount_with_subtotal()
            return cash_check

        elif self.so_type == 'lc_sales':
            return self.lc_sales_business_logics()



    def lc_sales_business_logics(self):

        # If LC and PI ref is present, go to the Final Approval
        # Else  ## go to Second level approval
        if self.lc_no and self.pi_no:
            if self.lc_no.lc_value == self.products_price_sum() \
                    or self.lc_no.lc_value > self.products_price_sum():

                return self.write({'state': 'close'})
            else:
                return self.write({'state': 'approve'})

        # 1. Has PI & no LC then go to second level approval
        # 2. Check 100MT checking for this product, company wise
        if self.pi_no and not self.lc_no:
            res = {}
            list = dict.fromkeys(set([val.product_id.product_tmpl_id.id for val in self.line_ids]),0)


            for line in self.line_ids:
                list[line.product_id.product_tmpl_id.id] = list[line.product_id.product_tmpl_id.id] + line.quantity
                product_temp_pool = self.env['product.template'].search([('id', '=',line.product_id.id)])


            for rec in list:


                ordered_qty_pool = self.env['ordered.qty'].search([('lc_no','=',False),
                                                                   ('company_id','=',self.company_id.id),
                                                                   ('product_id','=', rec)])

                product_temp_pool = self.env['product.template'].search([('id', '=',rec)])

                res['product_id'] = rec
                res['ordered_qty'] = list[rec]
                res['delivery_auth_no'] = self.id

                if not ordered_qty_pool:
                    res['available_qty'] = 100 - list[rec]
                    self.env['ordered.qty'].create(res)

                    if list[rec] > 100:
                        self.write({'state': 'approve'}) # Second Approval
                    else:
                        self.write({'state': 'close'}) # Final Approval

                elif ordered_qty_pool and not ordered_qty_pool.lc_no:
                    for order in ordered_qty_pool:
                        if list[rec] > order.available_qty:
                            res['available_qty'] = order.available_qty - list[rec]
                            self.write({'state': 'approve'})  # Second Approval
                            order.write(res)
                        else:
                            res['available_qty'] = order.available_qty - list[rec]
                            self.write({'state': 'close'})  # Final Approval
                            order.write(res)


                    # if list[rec] > 100:
                    #     # self.write({'state': 'approve'}) # second level
                    #     warningstr = warningstr + 'Product {0} has order quantity is {1} which is more than 100\n'.format(
                    #         pro_tmpl.name, list[rec])
                    #
                    # print warningstr
                    #raise Warning(warningstr)


    def products_price_sum(self):
        product_line_subtotal = 0
        for do_product_line in self.line_ids:
            product_line_subtotal = product_line_subtotal + do_product_line.price_subtotal

        return product_line_subtotal


    #@todo Need to refactor below method -- rabbi
    @api.one
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

    @api.one
    def payment_information_check(self):
        for cash_line in self.cash_ids:

            if cash_line.account_payment_id.sale_order_id.id != self.sale_order_id.id:
                raise UserError("%s Payment Information is of a different Sale Order!" % (cash_line.account_payment_id.display_name))
                break;

            if cash_line.account_payment_id.is_this_payment_checked == True:
                raise UserError("Payment Information entered is already in use: %s" % (cash_line.account_payment_id.display_name))
                break;


    def update_sale_order_da_qty(self):
        for da_line in self.line_ids:
            for sale_line in self.sale_order_id.order_line:
                # if self.quantity > sale_line.da_qty:
                #     raise ValidationError('You can order another {0} {1}'.format((sale_line.da_qty), (sale_line.product_uom.name)))

                update_da_qty = sale_line.da_qty - da_line.quantity
                sale_line.write({'da_qty': update_da_qty})

                # if update_da_qty == 0.00:
                #     break;



    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.line_ids.quantity < 0 or self.line_ids.quantity == 0.00:
            raise UserError("Qty can not be Zero or Negative value")

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
                                        'number':payments.cheque_no,
                                        }))

                self.cheque_ids = vals


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

    @api.one
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


    @api.one
    def action_process_unattached_payments(self):
        account_payment_pool = self.env['account.payment'].search(
            [('is_this_payment_checked', '=', False), ('sale_order_id', '=', self.sale_order_id.id)])

        val = []
        for cash_line in self.cash_ids:
            val.append(cash_line.account_payment_id.id)

        vals = []
        if account_payment_pool:
            for payments in account_payment_pool:
                if payments.id not in val:
                    vals.append((0, 0, {'account_payment_id': payments.id,
                                        'amount': payments.amount,
                                        'dep_bank': payments.deposited_bank,
                                        'branch': payments.bank_branch,
                                        'payment_date': payments.payment_date,
                                        }))

            self.cash_ids = vals



class OrderedQty(models.Model):
    _name='ordered.qty'
    _description='Store Product wise ordered qty to track max qty value'
   # _order = "delivery_auth_no,desc"

    product_id = fields.Many2one('product.product', string='Product')
    ordered_qty = fields.Float(string='Ordered Qty')
    available_qty = fields.Float(string='Allowed Qty', default=0.00) ## available_qty = max_qty - ordered_qty
    lc_no = fields.Many2one('letter.credit', string='LC No')
    delivery_auth_no = fields.Many2one('delivery.order', string='Delivery Authrozation ref')
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env['res.company']._company_default_get('product_sales_pricelist'), required=True)
