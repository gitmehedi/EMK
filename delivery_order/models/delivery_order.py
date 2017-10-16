from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import time,datetime

class SaleDeliveryOrder(models.Model):
    _name = 'delivery.order'
    _description = 'Delivery Order'
    _inherit = ['mail.thread']
    _rec_name='name'

    # def _current_employee(self):
    #     return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(string='Name', index=True)

    so_date = fields.Date('Sales Order Date', readonly=True)

    deli_address = fields.Char('Delivery Address', readonly=True,
                             states={'draft': [('readonly', False)]})
    """ All relations fields """

    sale_order_id = fields.Many2one('sale.order',string='Sale Order',
                                    required=True, readonly=True,states={'draft': [('readonly', False)]})
    parent_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade', readonly=True,
                             related='sale_order_id.partner_id')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True,
                                      related='sale_order_id.payment_term_id')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True)
    line_ids = fields.One2many('delivery.order.line', 'parent_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]})
    cash_ids = fields.One2many('cash.payment.line', 'pay_cash_id', string="Cash", readonly=True, invisible =True,
                               states={'draft': [('readonly', False)]})

    cheque_ids=  fields.One2many('cheque.payment.line', 'pay_cash_id', string="Cheque", readonly=True,
                               states={'draft': [('readonly', False)]})
    tt_ids = fields.One2many('tt.payment.line', 'pay_tt_id', string="T.T", readonly=True,
                                 states={'draft': [('readonly', False)]})
    lc_ids = fields.One2many('lc.payment.line', 'pay_lc_id', string="L/C", readonly=True,
                             states={'draft': [('readonly', False)]})

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

   # account_payment_id = fields.Many2one('account.payment', string='Payment Information', required=True)

    so_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sale Order Type')

    state = fields.Selection([
        ('draft', "To Submit"),
        ('validate', "To Approve"),
        ('approve', "Second Approval"),
        ('close', "Approved")
    ], default='draft')

    """ All functions """

    @api.multi
    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise UserError('You can not delete this.')
            order.line_ids.unlink()
        return super(SaleDeliveryOrder, self).unlink()

    @api.one
    def action_draft(self):
        self.state = 'draft'
        self.line_ids.write({'state':'draft'})

    @api.multi
    def action_approve(self):
        # account_payment_pool = self.env['account.payment'].search(
        #     [('is_this_payment_checked','=',False),('sale_order_id', '=', self.sale_order_id.id), ('partner_id', '=', self.parent_id.id)])

        # if not account_payment_pool:
        #     raise UserError("Either Payment Information not found for this Sale Order Or Payment Information entered is already in use")

        for cash_line in self.cash_ids:
            if cash_line.account_payment_id.is_this_payment_checked == True:
                raise UserError("Payment Information entered is already in use: %s" %(cash_line.account_payment_id.display_name))
                break;

        # delivery_order_pool = self.env['delivery.order'].search(
        #     [('state', '=', 'close'), ('cash_ids', '=', cash_line.account_payment_id.id),('sale_order_id', '=', self.sale_order_id.id)])

        if self.so_type == 'cash' :
            # and account_payment_pool.state == 'posted' \
            # and account_payment_pool \
            # and account_payment_pool.payment_type == 'inbound' \
            # and self.sale_order_id.id == account_payment_pool.sale_order_id.id:

            self.state = 'approve'
            self.line_ids.write({'state': 'approve'})
            self.approver2_id = self.env.user
            #account_payment_pool.write({'is_this_payment_checked':True})

            return self.write({'state': 'approve', 'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')})


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
        if self.sale_order_id:
            val = []
            sale_order_obj = self.env['sale.order'].search([('id', '=',self.sale_order_id.id)])

            if sale_order_obj:
                self.warehouse_id = sale_order_obj.warehouse_id.id
                self.so_type = sale_order_obj.credit_sales_or_lc
                self.so_date = sale_order_obj.confirmation_date

                for record in sale_order_obj.order_line:
                    val.append((0, 0, {'product_id': record.product_id.id,
                                       'quantity': record.product_uom_qty,
                                       'pack_type': sale_order_obj.pack_type.id,
                                       'uom_id': record.product_uom.id,
                                                }))

            self.line_ids = val
