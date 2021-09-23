from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DeliveryScheduleLine(models.Model):
    _name = 'delivery.schedules.line'
    _inherit = ['mail.thread']
    _description = 'Delivery Schedule line'

    schedule_id = fields.Many2one('delivery.schedules', 'Delivery Schedule')
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True, required=True,
                                 domain=[('customer', '=', True), ('parent_id', '=', False)],
                                 states={'draft': [('readonly', False)]})
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, readonly=True,
                                    states={'draft': [('readonly', False)]}, track_visibility='onchange')
    delivery_order_id = fields.Many2one('delivery.order', string='Pending Delivery Order', readonly=True, track_visibility='onchange')
    ordered_qty = fields.Float(string='Ordered Qty', readonly=True, store=True, compute='_compute_ordered_qty')
    undelivered_qty = fields.Float(string='Undelivered Qty', compute='_compute_undelivered_qty')
    scheduled_qty = fields.Float(string='Scheduled Qty.', readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)], 'revision': [('readonly', False)]})
    requested_date = fields.Date('Date', default=fields.Datetime.now)
    remarks = fields.Text('Special Instructions', readonly=True, track_visibility='onchange',
                          states={'draft': [('readonly', False)], 'revision': [('readonly', False)]})
    state = fields.Selection([
        ('draft', "Draft"),
        ('revision', "Revision"),
        ('approve', "Confirm"),
        ('done', "Done"),
        ('cancel', "Cancelled")
    ], default='draft', track_visibility='onchange')

    product_id = fields.Many2one('product.product', string='Product', readonly=True, track_visibility='onchange')
    uom_id = fields.Many2one('product.uom', string="UoM", readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', related='schedule_id.operating_unit_id',
                                        string='Operating Unit', store=True)

    # create date.................
    schedule_line_date = fields.Date('Date', default=fields.Datetime.now)

    unscheduled_qty = fields.Float(string='Unscheduled Qty', compute='_compute_unscheduled_qty')

    @api.depends('delivery_order_id')
    def _compute_undelivered_qty(self):
        for rec in self:
            if rec.delivery_order_id.line_ids:
                line = rec.delivery_order_id.line_ids[0]
                rec.undelivered_qty = line.quantity - line.qty_delivered

    @api.depends('product_id')
    def _compute_ordered_qty(self):
        for rec in self:
            lines = self.env['delivery.order.line'].search([('parent_id', '=', rec.delivery_order_id.id), ('product_id', '=', rec.product_id.id)])
            if lines:
                rec.ordered_qty = lines[0].quantity

    @api.depends('scheduled_qty')
    def _compute_unscheduled_qty(self):
        for rec in self:
            if rec.delivery_order_id:
                delivery_order_lines = self.env['delivery.order.line'].search([('parent_id', '=', rec.delivery_order_id.id), ('product_id', '=', rec.product_id.id)])
                delivery_schedules_lines = self.env['delivery.schedules.line'].search([('delivery_order_id', '=', rec.delivery_order_id.id), ('state', '!=', 'done')])
                total_scheduled_qty = sum(line.scheduled_qty for line in delivery_schedules_lines)
                rec.unscheduled_qty = delivery_order_lines[0].quantity - delivery_order_lines[0].qty_delivered - total_scheduled_qty

    @api.constrains('scheduled_qty')
    def _check_scheduled_qty(self):
        if self.scheduled_qty > self.undelivered_qty:
            raise ValidationError('Schedule quantity cannot be larger than Undelivered Qty.!')

        if self.scheduled_qty <= 0:
            raise ValidationError(_('Schedule quantity has to be strictly positive.'))

        if self.unscheduled_qty < 0:
            delivery_schedules_lines = self.env['delivery.schedules.line'].search(
                [('delivery_order_id', '=', self.delivery_order_id.id), ('state', '!=', 'done')])
            total_scheduled_qty = sum(line.scheduled_qty for line in delivery_schedules_lines)

            raise ValidationError(_('Scheduled qty cannot be greater than Undelivered Qty.\n'
                                    '\nSale Order: %s\nUndelivered Qty: %s\nScheduled Qty: %s\n') %
                                  (self.sale_order_id.name, self.undelivered_qty, total_scheduled_qty))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.sale_order_id = False
        # get sale order of which delivery authorization is approved
        delivery_authorizations = self.env['delivery.authorization'].sudo().search([
            ('sale_order_id.partner_id', '=', self.partner_id.id),
            ('operating_unit_id', '=', self.schedule_id.operating_unit_id.id),
            ('state', '=', 'close')
        ])

        sale_order_lines = delivery_authorizations.mapped('sale_order_id').mapped('order_line').filtered(
            lambda x: x.product_uom_qty > x.qty_delivered)
        sale_order_ids = sale_order_lines.mapped('order_id').filtered(
            lambda o: o.region_type == self.schedule_id.region_type)

        if len(sale_order_ids) == 1:
            self.sale_order_id = self.env['sale.order'].sudo().search([('id', '=', sale_order_ids.id)])

        return {'domain': {'sale_order_id': [('id', 'in', sale_order_ids.ids)]}}

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        self.delivery_order_id = False
        self.product_id = False
        self.uom_id = False
        self.ordered_qty = False
        self.scheduled_qty = False

        if self.sale_order_id:
            self.delivery_order_id = self.env['delivery.order'].sudo().search([
                ('sale_order_id', '=', self.sale_order_id.id),
                ('state', '=', 'approved')
            ], limit=1)
            if self.delivery_order_id.line_ids:
                line = self.delivery_order_id.line_ids[0]
                self.product_id = line.product_id
                self.uom_id = line.uom_id
                self.ordered_qty = line.quantity

    @api.model
    def create(self, vals):
        if 'delivery_order_id' not in vals:
            delivery_order = self.env['delivery.order'].sudo().search([('sale_order_id', '=', vals['sale_order_id']),
                                                                       ('state', '=', 'approved')])
            if not delivery_order:
                raise Warning(_('There is no pending delivery order.'))
            if not delivery_order.line_ids:
                raise Warning(_('There is no product line of pending delivery order.'))

            line = delivery_order.line_ids[0]

            vals['delivery_order_id'] = delivery_order.id
            vals['product_id'] = line.product_id.id
            vals['ordered_qty'] = line.quantity
            vals['uom_id'] = line.uom_id.id

        return super(DeliveryScheduleLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'sale_order_id' in vals:
            delivery_order = self.env['delivery.order'].sudo().search([('sale_order_id', '=', vals['sale_order_id']),
                                                                       ('state', '=', 'approved')])

            if not delivery_order:
                raise Warning(_('There is no pending delivery order.'))
            if not delivery_order.line_ids:
                raise Warning(_('There is no product line of pending delivery order.'))

            line = delivery_order.line_ids[0]

            vals['delivery_order_id'] = delivery_order.id
            vals['product_id'] = line.product_id.id
            vals['ordered_qty'] = line.quantity
            vals['uom_id'] = line.uom_id.id

        return super(DeliveryScheduleLine, self).write(vals)

    @api.multi
    def unlink(self):
        if any(rec.state == 'done' for rec in self):
            raise UserError(_('You cannot delete a record which is done state!'))

        return super(DeliveryScheduleLine, self).unlink()
