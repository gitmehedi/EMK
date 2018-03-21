from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
import datetime
import time
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ItemBorrowing(models.Model):
    _name = 'item.borrowing'
    _description = "Item Borrowing"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "issue_date desc"

    def _get_default_item_loan_borrow_location_id(self):
        return self.env['stock.location'].search([('scrap_location', '=', True)], limit=1).id

    def _get_default_location_id(self):
        return self.env['stock.location'].search([('operating_unit_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id

    name = fields.Char('Issue #', size=30, readonly=True, default="/")
    issue_date = fields.Datetime('Issue Date', required=True, readonly=True,
                                 default=datetime.datetime.today())
    issuer_id = fields.Many2one('res.users', string='Issuer', required=True, readonly=True,
                                default=lambda self: self.env.user,
                                states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string="Partner Company" ,readonly=True, required=True,
                                 states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    item_lines = fields.One2many('item.borrowing.line', 'item_borrowing_id', 'Items', readonly=True,
                                 states={'draft': [('readonly', False)]})

    location_id = fields.Many2one('stock.location', 'Location', default=_get_default_location_id,
                                  domain="[('usage', '=', 'internal'),('operating_unit_id', '=',operating_unit_id)]",
                                  required=True,
                                  states={'draft': [('readonly', False)]})
    item_loan_borrow_location_id = fields.Many2one('stock.location', 'Scrap Location',
                                            default=_get_default_item_loan_borrow_location_id,
                                            domain="[('scrap_location', '=', True)]", readonly=True)
    picking_id = fields.Many2one('stock.picking', 'Picking', states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
    request_by = fields.Many2one('res.users', string='Request By', required=True, readonly=True,
                                 default=lambda self: self.env.user)

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
                raise UserError(_('You cannot confirm %s which has no line.' % (loan.name)))
            res = {
                'state': 'waiting_approval',
            }
            seq = self.env['ir.sequence']
            seq_search = seq.search([('name','=','Item Loan Lending Test')])
            seq_search.sudo().write({'prefix':'Loan'+'/'+self.operating_unit_id.code+'/',
                              'code':self.operating_unit_id.name,
                              'operating_unit_id':self.operating_unit_id.id})

            new_seq = self.env['ir.sequence'].next_by_code('item.borrowing')

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
            'picking_id': picking_id
        }
        self.write(res)

    @api.model
    def _create_pickings_and_moves(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in self.item_lines:
            date_planned = datetime.datetime.strptime(self.issue_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    picking_type = self.env['stock.picking.type'].search(
                        [('default_location_src_id', '=', self.location_id.id),
                         ('default_location_dest_id', '=', self.item_loan_borrow_location_id.id), ('code', '=', 'internal')])
                    if not picking_type:
                        raise UserError(_('Please create picking type for product scraping.'))

                    pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
                    res = {
                        'picking_type_id': picking_type.id,
                        'priority': '1',
                        'move_type': 'direct',
                        'company_id': self.env.user['company_id'].id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'state': 'done',
                        'invoice_state': 'none',
                        'origin': self.name,
                        'name': pick_name,
                        'date': self.issue_date,
                        'partner_id': self.request_by.partner_id.id or False,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.item_loan_borrow_location_id.id,
                    }
                    if self.company_id:
                        vals = dict(res, company_id=self.company_id.id)

                    picking = picking_obj.create(vals)
                    if picking:
                        picking_id = picking.id

                location_id = self.location_id.id

                moves = {
                    'name': self.name,
                    'origin': self.name or self.picking_id.name,
                    'location_id': location_id,
                    'scrapped': True,
                    'location_dest_id': self.item_loan_borrow_location_id.id,
                    'picking_id': picking_id or False,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'picking_type_id': picking_type.id,

                }
                move = move_obj.create(moves)
                move.action_done()
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
        self.state = 'draft'
        self.item_lines.write({'state': 'draft'})


    ####################################################
    # Override methods
    ####################################################

class ItemBorrowingLines(models.Model):
    _name = 'item.borrowing.line'
    _description = 'Item Borrowing Line'


    item_borrowing_id = fields.Many2one('item.borrowing', string='Indent', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    product_uos_qty = fields.Float('Quantity (UoS)', digits=dp.get_precision('Product UoS'),
                                   default=1)
    product_uos = fields.Many2one('product.uom', 'Product UoS')
    price_unit = fields.Float('Price', digits=dp.get_precision('Product Price'),
                              help="Price computed based on the last purchase order approved.")
    name = fields.Text('Specification', store=True)
    sequence = fields.Integer('Sequence')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='State')

    ####################################################
    # Business methods
    ####################################################
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {'value': {'product_uom_qty': 1.0,
                              'product_uom': False,
                              'price_unit': 0.0,
                              'name': '',
                              }
                    }
        product_obj = self.env['product.product']
        product = product_obj.search([('id', '=', self.product_id.id)])

        product_name = product.name_get()[0][1]
        self.name = product_name
        self.product_uom = product.uom_id.id
        self.price_unit = product.standard_price


    ####################################################
    # Override methods
    ####################################################
