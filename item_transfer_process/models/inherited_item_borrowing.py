import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, frozendict


class InheritedItemBorrowing(models.Model):
    _inherit = 'item.borrowing'

    is_transfer = fields.Boolean(string='Is Transfer')
    item_transfer_send_id = fields.Many2one('item.loan.lending', string='Transfer')

    @api.multi
    def button_confirm_receive(self):
        for loan in self:
            if not loan.item_lines:
                raise UserError(_('You cannot confirm this without product.'))
            res = {
                'state': 'waiting_approval',
            }
            requested_date = datetime.strptime(self.request_date, "%Y-%m-%d %H:%M:%S").date()

            new_seq = self.env['ir.sequence'].next_by_code_new('item.borrowing.receive', requested_date)

            if new_seq:
                res['name'] = new_seq
            loan.write(res)
            loan.item_lines.write({'state': 'waiting_approval'})

    @api.multi
    def button_approve_receive(self):
        picking_id = False
        if self.item_lines:
            picking_id = self._create_pickings_and_moves_receive()
            picking_objs = self.env['stock.picking'].search([('id', '=', picking_id)])
            picking_objs.action_confirm()
            picking_objs.force_assign()
        res = {
            'state': 'approved',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'picking_id': picking_id
        }
        self.write(res)
        self.item_lines.write({'state': 'approved'})

    @api.model
    def _create_pickings_and_moves_receive(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in self.item_lines:
            date_planned = datetime.strptime(self.request_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('default_location_dest_id', '=', self.item_loan_borrow_location_id.id),
                         ('code', '=', 'operating_unit_transfer'),
                         ('default_location_src_id', '=', self.location_id.id)], limit=1)
                    if not picking_type:
                        raise UserError(_('Please create picking type for Item Borrowing.'))
                    res = {
                        'picking_type_id': self.picking_type_id.id,
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.company_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'state': 'draft',
                        'invoice_state': 'none',
                        'origin': self.name,
                        'name': self.name,
                        'date': self.request_date,
                        'partner_id': self.partner_id.id or False,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.item_loan_borrow_location_id.id,
                    }
                    self.picking_type_id = picking_type.id
                    picking = picking_obj.create(res)
                    if picking:
                        picking_id = picking.id

                location_id = self.location_id.id

                moves = {
                    'name': self.name,
                    'origin': self.name or self.picking_id.name,
                    'location_id': location_id,
                    'location_dest_id': self.item_loan_borrow_location_id.id,
                    'picking_id': picking_id or False,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'picking_type_id': picking_type.id,
                    'state': 'draft',

                }
                move_obj.create(moves)

        return picking_id



