import time
from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ItemBorrowing(models.Model):
    _name = 'item.borrowing'
    _description = "Item Borrowing"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "request_date desc"

    def _get_default_item_loan_borrow_location_id(self):
        return self.env['stock.location'].search([('operating_unit_id', '=', self.env.user.default_operating_unit_id.id),('name','=','Input')], limit=1).id

    def _get_default_location_id(self):
        return self.env['stock.location'].search([('usage', '=', 'supplier'),('can_loan_request', '=', True)], limit=1).id

    name = fields.Char('Issue #', size=100, readonly=True, default=lambda self: _('New'),track_visibility='onchange')
    request_date = fields.Datetime('Request Date', required=True, readonly=True,
                                 default=fields.Datetime.now,track_visibility='onchange')
    issuer_id = fields.Many2one('res.users', string='Issuer', required=True, readonly=True,
                                default=lambda self: self.env.user,track_visibility='onchange',
                                states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string="Partner Company" ,readonly=True, required=True,
                                 domain="[('is_company', '=', True),('parent_id', '=', False)]",track_visibility='onchange',
                                 states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    item_lines = fields.One2many('item.borrowing.line', 'item_borrowing_id', 'Items', readonly=True,
                                 states={'draft': [('readonly', False)]})
    location_id = fields.Many2one('stock.location', 'Source Location', default=_get_default_location_id,
                                  readonly = True,required=True,help="source location. from where item is borrowing.",
                                  states={'draft': [('readonly', False)]})
    item_loan_borrow_location_id = fields.Many2one('stock.location', 'Destination Location',required=True,
                                            default=_get_default_item_loan_borrow_location_id,
                                            domain="[('usage', '=', 'internal'),('operating_unit_id', '=',operating_unit_id)]",
                                            help="destination location.")
    picking_id = fields.Many2one('stock.picking', 'Picking', states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
    request_by = fields.Many2one('res.users', string='Request By', required=True, readonly=True,
                                 default=lambda self: self.env.user)
    approved_date = fields.Datetime('Approved Date', readonly=True,track_visibility='onchange')
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True,
                                  help="who have approve or reject.",track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
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
                raise UserError(_('You cannot confirm this without product.'))
            res = {
                'state': 'waiting_approval',
            }
            requested_date = datetime.strptime(self.request_date, "%Y-%m-%d %H:%M:%S").date()
            new_seq = self.env['ir.sequence'].next_by_code_new('item.borrowing',requested_date)

            if new_seq:
                res['name'] = new_seq
            loan.write(res)
            loan.item_lines.write({'state': 'waiting_approval'})

    @api.multi
    def button_approve(self):
        picking_id = False
        if self.item_lines:
            picking_id = self._create_pickings_and_moves()
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
    def _create_pickings_and_moves(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in self.item_lines:
            date_planned = datetime.strptime(self.request_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('default_location_dest_id', '=', self.item_loan_borrow_location_id.id),('code', '=', 'incoming'),
                         ('default_location_src_id', '=', self.location_id.id)],limit=1)
                    if not picking_type:
                        raise UserError(_('Please create picking type for Item Borrowing.'))
                    res = {
                        'picking_type_id': picking_type.id,
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

    @api.multi
    def button_reject(self):
        res = {
            'state': 'reject',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)
        self.item_lines.write({'state': 'reject'})

    @api.multi
    def action_draft(self):
        res = {
            'state': 'draft',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)
        self.item_lines.write({'state': 'draft'})

    @api.multi
    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = ['|',('id', '=', self.picking_id.id),('origin','=',self.name)]
        return action

    ####################################################
    # Override methods
    ####################################################

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete this !!'))
        return super(ItemBorrowing, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        if users_obj.has_group('stock.group_stock_manager'):
            domain = [
                ('state', 'in', ['waiting_approval'])]
            return domain
        else:
            return False

class ItemBorrowingLines(models.Model):
    _name = 'item.borrowing.line'
    _description = 'Item Borrowing Line'

    item_borrowing_id = fields.Many2one('item.borrowing', string='Item', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True,ondelete='cascade')
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one(related='product_id.uom_id',comodel='product.uom',string= 'Unit of Measure',
                                  required=True,store=True)
    price_unit = fields.Float(related='product_id.standard_price',string='Price', digits=dp.get_precision('Product Price'),
                              help="Price computed based on the last purchase order approved.",store=True)
    name = fields.Char(related='product_id.name',string='Specification',store=True)
    sequence = fields.Integer('Sequence')
    given_qty = fields.Float('Given Quantity', digits=dp.get_precision('Product UoS'))
    received_qty = fields.Float('Receive Quantity', digits=dp.get_precision('Product UoS'))
    due_qty = fields.Float(string='Due', digits=dp.get_precision('Product UoS'),
                           compute='_compute_due_quantity')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('receive', 'Receive'),
        ('reject', 'Rejected'),
    ], string='State')

    ####################################################
    # Business methods
    ####################################################

    @api.depends('given_qty', 'received_qty')
    @api.multi
    def _compute_due_quantity(self):
        for product_line in self:
            product_line.due_qty = product_line.received_qty - product_line.given_qty

    @api.one
    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        if self.product_uom_qty < 0:
            raise UserError('You can\'t give negative value!!!')

    ####################################################
    # Override methods
    ####################################################
