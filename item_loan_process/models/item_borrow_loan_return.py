from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ItemBorrowing(models.Model):
    _inherit = 'item.borrowing'

    return_picking_id = fields.Many2one('stock.picking', 'Picking')

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        # for product in self.item_lines:
        #     if product.due_qty <= 0:
        #         raise UserError('No Due so no need any adjustment!!!')

        if self.return_picking_id:
            pass
        else:
            self._create_return_pickings_and_moves()
            self.return_picking_id.action_confirm()
            self.return_picking_id.force_assign()

        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]
        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        pick_id = self.return_picking_id.id
        # choose the view_mode accordingly
        # if len(pick_ids) > 1:
        #     result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        # elif len(pick_ids) == 1:
        #     res = self.env.ref('stock.view_picking_form', False)
        #     result['views'] = [(res and res.id or False, 'form')]
        #     result['res_id'] = pick_ids and pick_ids[0] or False
        res = self.env.ref('stock.view_picking_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = pick_id or False
        return result

    @api.model
    def _create_return_pickings_and_moves(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in self.item_lines:
            date_planned = datetime.strptime(self.request_date, DEFAULT_SERVER_DATETIME_FORMAT)
            location_id = self.env['stock.location'].search(
                [('operating_unit_id', '=', self.env.user.default_operating_unit_id.id), ('name', '=', 'Stock')],
                limit=1).id
            location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1).id
            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('default_location_src_id', '=', location_id),
                         ('code', '=', 'outgoing')])
                    if not picking_type:
                        raise UserError(_('Please create picking type for Item Borrowing.'))
                    pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
                    res = {
                        'picking_type_id': picking_type.id,
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.env.user['company_id'].id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'state': 'draft',
                        'invoice_state': 'none',
                        'origin': 'Return/'+self.name,
                        'name': pick_name,
                        'date': self.request_date,
                        'partner_id': self.partner_id.id or False,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                    }
                    if self.company_id:
                        vals = dict(res, company_id=self.company_id.id)

                    picking = picking_obj.create(vals)
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
                move = move_obj.create(moves)
                # move.action_done()
                self.write({'move_id': move.id})

        self.return_picking_id = picking_id

        # self.return_picking_id.action_confirm()
        # self.return_picking_id.force_assign()
        return True

    # @api.multi
    # def _get_picking_id(self):
    #     picking_id = self.return_picking_id.id
    #     picking_obj = self.env['stock.picking']
    #     picking = picking_obj.browse(picking_id)
    #     if picking.state != 'done':
    #         return [picking.id]
    #     elif picking.state == 'done' and self.state == 'inprogress':
    #         picking_ids = picking_obj.search([('id', '=', picking_id)])
    #         return picking_ids.ids
    #     return False

    @api.multi
    def action_get_adjustment_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', '=', self.return_picking_id.id)]
        return action