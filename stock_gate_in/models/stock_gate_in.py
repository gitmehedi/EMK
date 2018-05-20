import datetime

from odoo import models, fields, api,_

class ProductGateIn(models.Model):
    _inherit = 'product.gate.in'

    picking_id = fields.Many2one('stock.picking', 'Picking')

    @api.multi
    def action_confirm(self):
        res = super(ProductGateIn, self).action_confirm()
        if self.shipping_line_ids:
            picking_id = self._create_pickings_and_procurements()
            picking_objs = self.env['stock.picking'].search([('id','=',picking_id)])
            picking_objs.action_confirm()
            picking_objs.force_assign()
            self.write({'picking_id': picking_id})
        return res

    @api.model
    def _create_pickings_and_procurements(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        location_obj = self.env['stock.location']
        picking_id = False
        for line in self.shipping_line_ids:
            date_planned = datetime.datetime.now()
            location_id = location_obj.search([('usage', '=', 'supplier')], limit=1)
            location_dest_id =location_obj.search([('operating_unit_id', '=', self.operating_unit_id.id),('name','=','Input')],limit=1)
            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('code', '=', 'incoming'),('warehouse_id.operating_unit_id', '=', self.operating_unit_id.id),
                         ('default_location_dest_id', '=', location_dest_id.id)])

                    pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
                    res = {
                        'receive_type': self.receive_type,
                        'transfer_type': 'receive',
                        'shipment_id': self.ship_id.id,
                        'picking_type_id': picking_type.id,
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.company_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'state': 'draft',
                        'name': self.name,
                        'date': date_planned,
                        'location_id': location_id.id,
                        'location_dest_id': location_dest_id.id,
                        'challan_bill_no': self.challan_bill_no,
                        'partner_id': self.partner_id.id,
                        'origin': self.name,
                    }
                    if self.company_id:
                        vals = dict(res, company_id=self.company_id.id)

                    picking = picking_obj.create(res)
                    if picking:
                        picking_id = picking.id

                moves = {
                    'name': self.name,
                    'origin': self.name or self.picking_id.name,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'picking_id': picking_id or False,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'picking_type_id': picking_type.id,
                    'state': 'draft',

                }
                move_obj.create(moves)

        return picking_id