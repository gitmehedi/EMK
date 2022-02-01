import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, frozendict


class InheritedItemLoanLending(models.Model):
    _inherit = 'item.loan.lending'

    @api.model
    def default_get(self, fields):
        res = super(InheritedItemLoanLending, self).default_get(fields)
        if 'default_is_transfer' in self._context:
            res['is_transfer'] = self._context.get('default_is_transfer')
            if res['is_transfer']:
                location_id = self.env['stock.location'].search(
                    [('usage', '=', 'transit'), ('can_operating_unit_transfer', '=', True)], limit=1).id
                if not location_id:
                    raise UserError(_('Destination location not found! Set Transit Location before sending items!'))
            else:
                location_id = self.env['stock.location'].search(
                    [('usage', '=', 'customer'), ('can_loan_request', '=', True)], limit=1).id

        else:
            location_id = self.env['stock.location'].search(
                [('usage', '=', 'customer'), ('can_loan_request', '=', True)], limit=1).id
        res['item_loan_location_id'] = location_id
        return res

    is_transfer = fields.Boolean(string='Is Transfer')

    @api.model
    def create(self, vals):
        # location_id will be based on operating unit
        if vals['is_transfer']:
            operating_unit_obj = self.env['operating.unit'].browse(vals['operating_unit_id'])
            vals['location_id'] = self.env['stock.location'].search(
                [('operating_unit_id', '=', operating_unit_obj.id), ('name', '=', 'Stock')], limit=1).id

        return super(InheritedItemLoanLending, self).create(vals)

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        return {'domain': {'receiving_operating_unit_id': [('company_id', '=', self.env.user.company_id.id),
                                                           ('id', '!=', self.operating_unit_id.id)]}}

    receiving_operating_unit_id = fields.Many2one('operating.unit')

    @api.onchange('receiving_operating_unit_id', 'operating_unit_id')
    def onchange_receiving_operating_unit_id(self):
        if self.receiving_operating_unit_id and self.operating_unit_id:
            if self.receiving_operating_unit_id.id == self.operating_unit_id.id:
                raise UserError(_('Source and Destination Operating Unit cannot be same!'))

    @api.onchange('issuer_id')
    def onchange_issuer_id(self):
        if self.issuer_id and self.is_transfer:
            if self.is_transfer:
                self.borrower_id = self.issuer_id.partner_id.id
            else:
                self.borrower_id = False

        else:
            self.borrower_id = False

    @api.model
    def _create_pickings_and_moves_for_item_sending(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        borrow_picking_id = False
        requested_date = datetime.strptime(self.request_date, "%Y-%m-%d %H:%M:%S").date()
        # creating loan borrow object
        new_seq = self.env['ir.sequence'].next_by_code_new('item.borrowing.receive', requested_date,
                                                           self.receiving_operating_unit_id)
        borrow_name = ''
        if new_seq:
            borrow_name = new_seq

        destination_loc_id = self.env['stock.location'].search(
            [('operating_unit_id', '=', self.receiving_operating_unit_id.id), ('name', '=', 'Input')],
            limit=1).id

        receiving_picking_type = self.env['stock.picking.type'].suspend_security().search(
            [('default_location_src_id', '=', self.item_loan_location_id.id),
             ('code', '=', 'operating_unit_transfer'),
             ('default_location_dest_id', '=', destination_loc_id),
             ('operating_unit_id', '=', self.receiving_operating_unit_id.id)])
        if not receiving_picking_type:
            raise UserError(
                _('Please create "Incoming" picking type for Item Receiving - ' + self.receiving_operating_unit_id.name))

        borrow_picking = self.env['item.borrowing'].suspend_security().create({
            'name': borrow_name,

            'issuer_id': self.issuer_id.id,
            'is_transfer': self.is_transfer,
            'item_transfer_send_id': self.id,
            'request_date': self.request_date,
            'partner_id': self.company_id.partner_id.id,
            'description': self.description,
            'location_id': receiving_picking_type.default_location_src_id.id,
            'item_loan_borrow_location_id': receiving_picking_type.default_location_dest_id.id,
            'company_id': self.company_id.id,
            'operating_unit_id': self.receiving_operating_unit_id.id,
            'picking_type_id': receiving_picking_type.id,
            'priority': '1',
            'state': 'draft'

        })

        for line in self.item_lines:
            date_planned = datetime.strptime(self.request_date, DEFAULT_SERVER_DATETIME_FORMAT)
            if line.product_id:
                if not picking_id:

                    picking_type = self.env['stock.picking.type'].search(
                        [('default_location_src_id', '=', self.location_id.id),
                         ('code', '=', 'operating_unit_transfer'),
                         ('default_location_dest_id', '=', self.item_loan_location_id.id),
                         ('operating_unit_id', '=', self.operating_unit_id.id)])
                    if not picking_type:
                        raise UserError(
                            ('Please create "Outgoing" picking type for Item Sending - ' + self.operating_unit_id.name))

                    res = {
                        'picking_type_id': picking_type.id,
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.env.user['company_id'].id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'state': 'draft',
                        'invoice_state': 'none',
                        'origin': self.name,
                        'name': self.name,
                        'date': self.request_date,
                        'date_done': self.request_date,
                        'partner_id': self.borrower_id.id or False,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.item_loan_location_id.id,
                    }
                    if self.company_id:
                        vals = dict(res, company_id=self.company_id.id)
                    picking = picking_obj.create(vals)
                    if picking:
                        picking_id = picking.id

                location_id = self.location_id.id

                moves = {
                    'name': self.name,
                    'origin': self.name,
                    'location_id': location_id,
                    'location_dest_id': self.item_loan_location_id.id,
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

                if borrow_picking:
                    borrow_line_obj = self.env['item.borrowing.line'].suspend_security().create({
                        'item_borrowing_id': borrow_picking.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'price_unit': line.price_unit,
                        'name': line.product_id.name,
                        'given_qty': line.given_qty,
                        'received_qty': line.received_qty,
                        'due_qty': line.due_qty,
                        'state': 'draft'
                    })

        return picking_id

    def button_approve_for_sending(self):
        picking_id = False
        if self.item_lines:
            picking_id = self._create_pickings_and_moves_for_item_sending()
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

    @api.multi
    def button_confirm_for_sending(self):
        for loan in self:
            if not loan.item_lines:
                raise UserError(_('You cannot confirm this without product.'))

            picking_type = self.env['stock.picking.type'].search(
                [('default_location_src_id', '=', self.location_id.id),
                 ('code', '=', 'operating_unit_transfer'),
                 ('default_location_dest_id', '=', self.item_loan_location_id.id),
                 ('operating_unit_id', '=', self.operating_unit_id.id)])
            if not picking_type:
                raise UserError(
                    ('Please create "Outgoing" picking type for Item Sending - ' + self.operating_unit_id.name))

            res = {
                'state': 'waiting_approval',
                'picking_type_id': picking_type.id
            }
            requested_date = datetime.strptime(self.request_date, "%Y-%m-%d %H:%M:%S").date()
            new_seq = self.env['ir.sequence'].next_by_code_new('item.loan.lending.send', requested_date,
                                                               self.operating_unit_id)
            if new_seq:
                res['name'] = new_seq
            loan.write(res)
            loan.item_lines.write({'state': 'waiting_approval'})
