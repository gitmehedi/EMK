from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
import datetime
import time
from odoo.exceptions import UserError, ValidationError

class ItemLoanLending(models.Model):
    _name = 'item.loan.lending'
    _description = "Item Loan Lending"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "issue_date desc"

    def _get_default_location_id(self):
        return self.env['stock.location'].search([('operating_unit_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id

    name = fields.Char('Issue #', size=30, readonly=True, default=lambda self: _('New'),copy=False,
                       states={'draft': [('readonly', False)]})
    issue_date = fields.Datetime('Issue Date', required=True, readonly=True,
                                  default=datetime.datetime.today())
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
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    item_lines = fields.One2many('item.loan.lending.line', 'item_loan_lending_id', 'Items', readonly=True,
                                    states={'draft': [('readonly', False)]})
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
            new_seq = self.env['ir.sequence'].next_by_code('item.loan.lending')
            if new_seq:
                res['name'] = new_seq
            loan.write(res)

    @api.multi
    def button_approve(self):
        for item in self:
            for line in item.item_lines:
                if line.product_uom_qty > line.qty_available:
                    raise UserError(_(
                    'You cannot give loan without having available stock for %s. '
                    'You can correct it with an inventory adjustment.') % line.product_id.name)
            res = {
                'state': 'approved',
                'approver_id': self.env.user.id,
                'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            item.write(res)

    @api.multi
    def button_reject(self):
        res = {
            'state': 'reject',
            'approver_id': self.env.user.id,
            'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)

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

    item_loan_lending_id = fields.Many2one('indent.indent', string='Indent', required=True, ondelete='cascade')
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
    ####################################################
    # Override methods
    ####################################################