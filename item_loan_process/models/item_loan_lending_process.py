from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
import time
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ItemLoanLending(models.Model):
    _name = 'item.loan.lending'
    _description = "Item Loan Lending"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "request_date desc"


    def _get_default_item_loan_location_id(self):
        return self.env['stock.location'].search([('usage', '=', 'customer')], limit=1).id

    def _get_default_location_id(self):
        return self.env['stock.location'].search([('operating_unit_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id

    name = fields.Char('Issue #', size=30, readonly=True, default=lambda self: _('New'),copy=False,
                       states={'draft': [('readonly', False)]})
    request_date = fields.Datetime('Request Date', required=True, readonly=True,
                                  default=datetime.today())
    issuer_id = fields.Many2one('res.users', string='Issue By', required=True, readonly=True,
                                  default=lambda self: self.env.user,states={'draft': [('readonly', False)]})
    borrower_id = fields.Many2one('res.partner', string="Request By" ,readonly=True, required=True,
                                  states={'draft': [('readonly', False)]})
    approved_date = fields.Datetime('Approved Date', readonly=True)
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True,
                                  help="who have approve or reject.")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    location_id = fields.Many2one('stock.location', 'Location', default=_get_default_location_id,
                                  domain="[('usage', '=', 'internal'),('operating_unit_id', '=',operating_unit_id)]",
                                  required=True,
                                  states={'draft': [('readonly', False)]})
    item_loan_location_id = fields.Many2one('stock.location', 'Destination Location', default=_get_default_item_loan_location_id,
                                            readonly=True)
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    item_lines = fields.One2many('item.loan.lending.line', 'item_loan_lending_id', 'Items', readonly=True,
                                    states={'draft': [('readonly', False)]})

    picking_id = fields.Many2one('stock.picking', 'Picking', states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
    request_by = fields.Many2one('res.users', string='Request By', required=True, readonly=True,
                                 default=lambda self: self.env.user)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True, copy=False, track_visibility='onchange', default='draft')

    ####################################################
    # Business methods
    ####################################################
    @api.multi
    def button_confirm(self):
        for loan in self:
            if not loan.item_lines:
                raise UserError(_('You cannot confirm %s which has no line.' % (loan.name)))
            res = {
                'state': 'waiting_approval',
            }
            requested_date = datetime.strptime(self.request_date, "%Y-%m-%d %H:%M:%S").date()
            new_seq = self.env['ir.sequence'].next_by_code_new('item.loan.lending',requested_date)
            if new_seq:
                res['name'] = new_seq
            loan.write(res)

    @api.multi
    def button_approve(self):
        picking_id = False
        if self.item_lines:
            picking_id = self._create_pickings_and_moves()
        res = {
            'state': 'approved',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'picking_id' : picking_id
        }
        self.write(res)

    @api.model
    def _create_pickings_and_moves(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in self.item_lines:
            date_planned = datetime.strptime(self.request_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('default_location_src_id', '=', self.location_id.id),
                         ('default_location_dest_id', '=', self.item_loan_location_id.id), ('code', '=', 'outgoing')])
                    if not picking_type:
                        raise UserError(_('Please create picking type for Item Landing.'))
                    # pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
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
                move = move_obj.create(moves)
                # move.action_done()
                self.write({'move_id': move.id})

        return picking_id

    @api.multi
    def button_reject(self):
        res = {
            'state': 'reject',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)

    @api.multi
    def action_draft(self):
        res = {
            'state': 'draft',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)
        self.item_lines.write({'state': 'draft'})

    ####################################################
    # ORM Overrides methods
    ####################################################

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete this !!'))
        return super(ItemLoanLending, self).unlink()

class ItemLoanLendingLines(models.Model):
    _name = 'item.loan.lending.line'
    _description = 'Item Loan Lending Line'

    item_loan_lending_id = fields.Many2one('item.loan.lending', string='Item', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    qty_available = fields.Float('In Stock', compute='_computeProductQuentity', store=True)
    name = fields.Text('Specification', store=True)
    sequence = fields.Integer('Sequence')

    ####################################################
    # Business methods
    ####################################################

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {'value': {'product_uom_qty': 1.0,
                              'product_uom': False,
                              'qty_available': 0.0,
                              'name': '',
                              }
                    }
        product_obj = self.env['product.product']
        product = product_obj.search([('id', '=', self.product_id.id)])

        product_name = product.name_get()[0][1]
        self.name = product_name
        self.product_uom = product.uom_id.id

    @api.depends('product_id')
    @api.multi
    def _computeProductQuentity(self):
        for productLine in self:
            if productLine.product_id.id:
                location_id = productLine.item_loan_lending_id.location_id.id
                product_quant = self.env['stock.quant'].search(['&', ('product_id', '=', productLine.product_id.id),
                                                                ('location_id', '=', location_id)], limit=1)
                if product_quant:
                    productLine.qty_available = product_quant.qty

    @api.one
    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        if self.product_uom_qty <= 0:
            raise UserError('Product quantity can not be negative or zero!!!')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='State')
    ####################################################
    # Override methods
    ####################################################