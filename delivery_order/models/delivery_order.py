from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import time, datetime


class DeliveryOrder(models.Model):
    _name = 'delivery.order'
    _description = 'Delivery Order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string='Name', index=True, readonly=True)

    delivery_order_id = fields.Many2one('delivery.authorization', string='DA No',
                                        domain=[('state', '=', 'close')],
                                        readonly=True, states={'draft': [('readonly', False)]})

    def _get_sale_order_currency(self):
        self.currency_id = self.sale_order_id.currency_id

    currency_id = fields.Many2one('res.currency', string='Currency', compute='_get_sale_order_currency',readonly=True, states={'draft': [('readonly', False)]})
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True, states={'draft': [('readonly', False)]})
    so_date = fields.Datetime('Order Date', readonly=True, states={'draft': [('readonly', False)]})
    deli_address = fields.Char('Delivery Address', readonly=True, states={'draft': [('readonly', False)]})

    parent_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade', readonly=True,
                                related='delivery_order_id.sale_order_id.partner_id',track_visibility='onchange')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True,
                                      related='delivery_order_id.sale_order_id.payment_term_id')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True,
                                   states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('delivery.order.line', 'parent_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]})
    cash_ids = fields.One2many('cash.payment.line.layer', 'pay_cash_id', string="Cash", readonly=True, invisible=True,
                               states={'draft': [('readonly', False)]})
    cheque_ids = fields.One2many('cheque.payment.line.layer', 'pay_cash_id', string="Cheque", readonly=True,
                                 states={'draft': [('readonly', False)]})
    tt_ids = fields.One2many('tt.payment.line', 'pay_tt_id', string="T.T", readonly=True,
                             states={'draft': [('readonly', False)]})
    lc_ids = fields.One2many('lc.payment.line', 'pay_lc_id', string="L/C", readonly=True,
                             states={'draft': [('readonly', False)]})
    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True,
                                   default=lambda self: self.env.user)

    requested_date = fields.Date(string="Requested Date", default=datetime.date.today(), readonly=True)

    so_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sales Type', readonly=True, states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', "Submit"),
        ('approved', "Approved"),
    ], default='draft',track_visibility='onchange')

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')


    @api.multi
    @api.depends('delivery_order_id.sale_order_id.procurement_group_id')
    def _compute_picking_ids(self):
        for order in self.delivery_order_id.sale_order_id:
            order.picking_ids = self.env['stock.picking'].search(
                [('group_id', '=', order.procurement_group_id.id)]) if order.procurement_group_id else []
            self.delivery_count = len(order.picking_ids)


    """ PI and LC """
    pi_id = fields.Many2one('proforma.invoice', string='PI Ref. No.', compute="_calculate_pi_id", store=False)
    lc_id = fields.Many2one('letter.credit', string='LC Ref. No.', readonly=True, compute = "_calculate_lc_id", store= False)

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', readonly=True)

    @api.multi
    def _calculate_pi_id(self):
        for _pi in self:
            _pi.pi_id = _pi.sale_order_id.pi_id.id


    @api.multi
    def _calculate_lc_id(self):
        for _do in self:
            _do.lc_id = _do.sale_order_id.lc_id.id

    """ All functions """

    @api.multi
    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise UserError('You can not delete record which is in Approved state')
            order.line_ids.unlink()
        return super(DeliveryOrder, self).unlink()


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('delivery.order') or '/'
        vals['name'] = seq

        return super(DeliveryOrder, self).create(vals)



    """ DO button box action """

    @api.multi
    def action_view_delivery(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.sale_order_id.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action


    @api.multi
    def create_delivery_order(self):

        ## Show or Create DO Button
        for order in self.sale_order_id:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if order.env.context.get('send_email'):
                order.force_quotation_send()
            order.order_line.sudo()._action_procurement_create()
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.sale_order_id.sudo().action_done()

        # Update the reference of Delivery Order and LC No to Stock Picking
        stock_picking_id = self.delivery_order_id.sale_order_id.picking_ids
        stock_picking_id.sudo().write({'delivery_order_id': self.id})

        # Update the reference of PI and LC on both Stock Picking and Sale Order Obj
        if self.delivery_order_id.so_type == 'lc_sales':
            stock_picking_id.sudo().write({'lc_id': self.lc_id.id})
            #self.delivery_order_id.sale_order_id.write({'lc_id': self.lc_id.id, 'pi_id': self.pi_id.id})
            #As per decision, LC Id will be updated to Sale Order from LC creation menu -- rabbi
            self.delivery_order_id.sale_order_id.sudo().write({'pi_id': self.pi_id.id})

        # Update Stock Move with reference of Delivery Order
        stock_move_id = self.delivery_order_id.sale_order_id.picking_ids.move_lines
        stock_move_id.sudo().write({'delivery_order_id': self.id})

        return True


    @api.onchange('delivery_order_id')
    def onchange_sale_order_id(self):
        delivery_auth_id = self.env['delivery.authorization'].search([('id', '=', self.delivery_order_id.id)])
        self.set_products_info_automatically(delivery_auth_id)


    @api.multi
    def set_products_info_automatically(self, delivery_auth_id):
        if self.delivery_order_id:
            val = []

            if delivery_auth_id:
                self.warehouse_id = delivery_auth_id.warehouse_id.id
                self.so_type = delivery_auth_id.so_type
                self.so_date = delivery_auth_id.so_date
                self.deli_address = delivery_auth_id.deli_address
                self.pi_id = delivery_auth_id.pi_id.id
                self.lc_id = delivery_auth_id.lc_id.id
                self.sale_order_id = delivery_auth_id.sale_order_id.id
                self.amount_untaxed = delivery_auth_id.amount_untaxed
                self.tax_value = delivery_auth_id.tax_value
                self.total_amount = delivery_auth_id.total_amount
                self.currency_id = delivery_auth_id.currency_id

                for record in delivery_auth_id.line_ids:

                    val.append((0, 0, {'product_id': record.product_id.id,
                                       'quantity': record.quantity,
                                       'pack_type': record.pack_type.id,
                                       'uom_id': record.uom_id.id,
                                       'commission_rate': record.commission_rate,
                                       'price_unit': record.price_unit,
                                       'price_subtotal': record.price_subtotal,
                                       'tax_id': record.tax_id.id,

                                       }))

            self.line_ids = val


    ### Showing batch
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