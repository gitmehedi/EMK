from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ItemBorrowing(models.Model):
    _inherit = 'item.borrowing'

    @api.model
    def _create_pickings_and_moves(self):
        res = super(ItemBorrowing, self)._create_pickings_and_moves()
        if res:
            picking_objs = self.env['stock.picking'].search([('id', '=', res)])
            picking_objs.write({'transfer_type': 'loan','receive_type': 'loan'})
        return res

    # return_picking_ids = fields.Many2many('stock.picking','picking_loan_rel','loan_id','picking_id','Picking(s)')
    return_picking_id = fields.Many2one('stock.picking','Return Picking')

    @api.multi
    def action_view_picking(self):

        product_list = self.item_lines.filtered(lambda o: o.due_qty > 0.0 )

        if not product_list:
            raise UserError('No Due so no need any adjustment!!!')
        # else:
        #     self.write({'return_picking_id': False})

        if not self.return_picking_id:
            self._create_return_pickings_and_moves(product_list)
            self.return_picking_id.action_confirm()
            self.return_picking_id.force_assign()
        else:
            pass


        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]
        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        pick_objs = self.env['stock.picking'].search([('backorder_id', '=', self.return_picking_id.id)])
        if pick_objs:
            pick_ids = pick_objs.ids + self.return_picking_id.ids
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        else:
            pick_id = self.return_picking_id.id
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_id or False
        return result

    @api.model
    def _create_return_pickings_and_moves(self,product_list):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in product_list:
            date_planned = datetime.strptime(self.request_date, DEFAULT_SERVER_DATETIME_FORMAT)
            location_id = self.env['stock.location'].search(
                [('operating_unit_id', '=', self.operating_unit_id.id), ('name', '=', 'Stock')],
                limit=1).id
            location_dest_id = self.location_id.id
            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('default_location_src_id', '=', location_id),
                         ('default_location_dest_id', '=', location_dest_id),
                         ('code', '=', 'loan_outgoing')], limit=1)
                    if not picking_type:
                        raise UserError(_('Please create picking type for Returning.'))
                    pick_name = self.env['stock.picking.type'].browse(picking_type.id).sequence_id.next_by_id()
                    res = {
                        'picking_type_id': picking_type.id,
                        'transfer_type': 'loan',
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.company_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'state': 'draft',
                        'invoice_state': 'none',
                        'origin': 'RETURN/'+self.name,
                        'name': pick_name,
                        'date': self.request_date,
                        'partner_id': self.partner_id.id or False,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                    }
                    picking = picking_obj.create(res)
                    if picking:
                        picking_id = picking.id

                moves = {
                    'name': line.name,
                    'origin': picking.name,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'picking_id': picking_id or False,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.due_qty,
                    'product_uom': line.product_uom.id,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'picking_type_id': picking_type.id,
                    'state': 'draft',

                }
                move_obj.create(moves)
        self.return_picking_id = picking_id

        return True

    # query = """INSERT INTO picking_loan_rel (loan_id,picking_id) VALUES (%s, %s) """
    # self._cr.execute(query, tuple([self.id, picking_id]))

    # @api.multi
    # def action_get_adjustment_picking(self):
    #     action = self.env.ref('stock.action_picking_tree_all').read([])[0]
    #     action['domain'] = [('id', '=', self.return_picking_id.id)]
    #     return action