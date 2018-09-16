from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DeliveryScheduleLine(models.Model):
    _name = 'delivery.schedules.line'
    _inherit = ['mail.thread']
    _description = 'Delivery Schedule line'

    parent_id = fields.Many2one('delivery.schedules', 'Delivery Schedule')
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True),('parent_id', '=', False)],
                                 readonly=True,required=True, states={'draft': [('readonly', False)]})
    pending_do = fields.Many2one('delivery.order',required=True,
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 string='Pending D.O',track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product',required=True,
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='onchange')
    do_qty = fields.Float(string='Ordered Qty', readonly=True ,store=True,compute='onchange_product_id')
    undelivered_qty = fields.Float(string='Undelivered Qty', readonly=True)
    uom_id = fields.Many2one('product.uom', string="Unit of Measure", readonly=True)
    scheduled_qty = fields.Float(string='Scheduled Qty.', readonly=True,
                                 states={'draft': [('readonly', False)],'revision': [('readonly', False)]},
                                 track_visibility='onchange')
    remarks = fields.Text('Special Instructions', readonly=True,
                          states={'draft': [('readonly', False)],'revision': [('readonly', False)]},
                          track_visibility='onchange')
    requested_date = fields.Date('Date',default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', "Draft"),
        ('revision', "Revision"),
        ('approve', "Confirm"),
        ('done', "Done"),
    ], default='draft', track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit',
                                        related='parent_id.operating_unit_id',
                                        string='Operating Unit',store=True)

    # create date.................
    schedule_line_date = fields.Date('Date',default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        line_obj = self.env['delivery.order.line'].search(
            [('parent_id', '=', vals['pending_do']), ('product_id', '=', vals['product_id'])])
        vals['do_qty'] = line_obj.quantity
        vals['undelivered_qty'] = line_obj.quantity - line_obj.qty_delivered
        vals['uom_id'] = line_obj.uom_id.id
        return super(DeliveryScheduleLine, self).create(vals)

    @api.multi
    def write(self, vals):
        line_obj = self.env['delivery.order.line'].search(
            [('parent_id', '=', self.pending_do.id), ('product_id', '=', self.product_id.id)])
        vals['do_qty'] = line_obj.quantity
        vals['undelivered_qty'] = line_obj.quantity - line_obj.qty_delivered
        vals['uom_id'] = line_obj.uom_id.id
        return super(DeliveryScheduleLine, self).write(vals)

    @api.multi
    def unlink(self):
        for entry in self:
            if entry.state != 'draft':
                raise UserError(_('After confirmation You can not delete this.'))
        return super(DeliveryScheduleLine, self).unlink()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for ds in self:
            ds.pending_do = []
            ds.product_id = []
            do_id_list = []
            if ds.partner_id:
                do_objs = self.env['delivery.order'].sudo().search([('parent_id','=',ds.partner_id.id),
                                                                    ('operating_unit_id','=',ds.parent_id.operating_unit_id.id),
                                                                    ('state','=','approved')])
                if do_objs:
                    for do_obj in do_objs:
                        do_line_list =  do_obj.line_ids.filtered(lambda x: x.quantity > x.qty_delivered)
                        if do_line_list:
                            do_id_list.append(do_obj.id)

                if len(do_id_list) == 1:
                    self.pending_do = self.env['delivery.order'].sudo().search([('id','=',do_id_list)])
                    return {'domain': {'pending_do': [('id', '=', do_id_list)]}}
                else:
                    return {'domain': {'pending_do': [('id', 'in', do_id_list)]}}

    @api.onchange('pending_do')
    def onchange_pending_do(self):
        for ds in self:
            if ds.pending_do:
                if len(ds.pending_do.line_ids) == 1:
                    ds.product_id = ds.pending_do.line_ids[0].product_id
                    ds.do_qty = ds.pending_do.line_ids[0].quantity
                    ds.undelivered_qty = ds.pending_do.line_ids[0].quantity - ds.pending_do.line_ids[0].qty_delivered
                    ds.uom_id = ds.pending_do.line_ids[0].uom_id

                    return {'domain': {'product_id': [('id', '=', ds.product_id.id)]}}
                else:
                    product_list = []
                    for line in ds.pending_do.line_ids:
                        product_list.append(line.product_id.id)
                    return {'domain': {'product_id': [('id', 'in', product_list)]}}

    @api.onchange('product_id')
    def onchange_product_id(self):
        for ds in self:
            ds.do_qty = False
            ds.undelivered_qty = False
            ds.uom_id = False
            ds.scheduled_qty = False
            ds.remarks = False
            if ds.product_id:
                line_obj = self.env['delivery.order.line'].search(
                    [('parent_id', '=', ds.pending_do.id), ('product_id', '=', ds.product_id.id)])[0]
                ds.do_qty = line_obj.quantity
                ds.undelivered_qty = line_obj.quantity - line_obj.qty_delivered
                ds.uom_id = line_obj.uom_id

    @api.multi
    def action_approve(self):
        for ds in self:
            ds.write({'state': 'done',})

    @api.constrains('scheduled_qty')
    def _check_scheduled_qty(self):
        for ds in self:
            if ds.scheduled_qty > ds.undelivered_qty:
                raise Warning('Schedule quantity can not larger than Undelivered Qty.!')
            elif self.scheduled_qty <= 0:
                raise ValueError(_('Schedule quantity has to be strictly positive.'))