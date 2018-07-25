from odoo import api, fields, models
from odoo.exceptions import ValidationError
import time, datetime


class DeliveryScheduleLine(models.Model):
    _name = 'delivery.schedules.line'
    _description = 'Delivery Schedule line'

    partner_id = fields.Many2one('res.partner', 'Customer', domain="([('customer','=','True')])")
    pending_do = fields.Many2one('stock.picking', string='Pending D.O', )  # domain="([('state','=','assigned')])"
    do_qty = fields.Float(string='Ordered Qty', readonly=True)
    undelivered_qty = fields.Float(string='Undelivered Qty', readonly=True)
    uom_id = fields.Many2one('product.uom', string="Unit of Measure", readonly=True)
    scheduled_qty = fields.Float(string='Scheduled Qty.')
    remarks = fields.Text('Special Instructions')

    # Relational Fields
    parent_id = fields.Many2one('delivery.schedules', ondelete='cascade')

    @api.model
    def _default_operating_unit(self):
        team = self.env['crm.team']._get_default_team_id()
        if team.operating_unit_id:
            return team.operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',
                                        required=True,
                                        default=_default_operating_unit)

    schedule_line_date = fields.Date('Date', default=datetime.date.today(), )


    @api.model
    def create(self, vals):
        picking_obj = self.env['stock.picking'].search([('id', '=', vals['pending_do'])])
        if picking_obj:
            vals['do_qty'] = picking_obj.sale_id.order_line.product_uom_qty
            vals['undelivered_qty'] = vals['do_qty'] - picking_obj.sale_id.order_line.qty_delivered
            vals['uom_id'] = picking_obj.sale_id.order_line.product_uom.id

        return super(DeliveryScheduleLine, self).create(vals)


    @api.multi
    def write(self, vals):

        picking_obj = self.env['stock.picking'].search([('id', '=', self.pending_do.id)])
        if picking_obj:
            vals['do_qty'] = picking_obj.sale_id.order_line.product_uom_qty
            vals['undelivered_qty'] = vals['do_qty'] - picking_obj.sale_id.order_line.qty_delivered
            vals['uom_id'] = picking_obj.sale_id.order_line.product_uom.id

        return super(DeliveryScheduleLine, self).write(vals)


    @api.onchange('pending_do')
    def onchange_pending_do(self):
        if self.pending_do.partner_id:
            # For the time being no loop, test purpose
            self.do_qty = self.pending_do.sale_id.order_line.product_uom_qty
            self.undelivered_qty = self.do_qty - self.pending_do.sale_id.order_line.qty_delivered
            self.uom_id = self.pending_do.sale_id.order_line.product_uom

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for ds in self:
            if ds.partner_id:
                stock_picking_obj = ds.env['stock.picking'].search(
                    [('partner_id', '=', ds.partner_id.id), ('state', '=', 'assigned')])

                if stock_picking_obj:
                    for s_picking in stock_picking_obj:
                        ds.pending_do = s_picking.id
