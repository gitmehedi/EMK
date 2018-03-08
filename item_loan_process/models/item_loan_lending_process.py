from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
import datetime
from odoo.exceptions import UserError, ValidationError

class ItemLoanLending(models.Model):
    _name = 'item.loan.lending'
    _description = "Item Loan Lending"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "issue_date desc"

    name = fields.Char('Issue #', size=30, readonly=True, default="/")
    issue_date = fields.Datetime('Issue Date', required=True, readonly=True,
                                  default=datetime.datetime.today())
    issuer_id = fields.Many2one('res.users', string='Issuer', required=True, readonly=True,
                                  default=lambda self: self.env.user,
                                  states={'draft': [('readonly', False)]})
    borrower_id = fields.Many2one('res.partner', string="Borrower Company" ,readonly=True, required=True,
                                  states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    item_lines = fields.One2many('item.loan.lending.line', 'item_loan_lending_id', 'Items', readonly=True,
                                    states={'draft': [('readonly', False)]})
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
            new_seq = self.env['ir.sequence'].next_by_code('item.loan.lending')
            if new_seq:
                res['name'] = new_seq
            loan.write(res)

    @api.multi
    def button_approve(self):
        res = {
            'state': 'approved',
        }
        self.write(res)

    @api.multi
    def button_reject(self):
        res = {
            'state': 'reject',
        }
        self.write(res)

    ####################################################
    # Override methods
    ####################################################

class ItemLoanLendingLines(models.Model):
    _name = 'item.loan.lending.line'
    _description = 'Item Loan Lending Line'

    item_loan_lending_id = fields.Many2one('indent.indent', string='Indent', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    product_uos_qty = fields.Float('Quantity (UoS)', digits=dp.get_precision('Product UoS'),
                                   default=1)
    product_uos = fields.Many2one('product.uom', 'Product UoS')
    price_unit = fields.Float('Price', digits=dp.get_precision('Product Price'),
                              help="Price computed based on the last purchase order approved.")
    price_subtotal = fields.Float(string='Subtotal', compute='_amount_subtotal', digits=dp.get_precision('Account'),
                                  store=True)
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
                              'price_unit': 0.0,
                              'name': '',
                              }
                    }
        product_obj = self.env['product.product']
        product = product_obj.search([('id', '=', self.product_id.id)])

        product_name = product.name_get()[0][1]
        self.name = product_name
        self.product_uom = product.uom_id.id
        self.price_unit = product.list_price
    ####################################################
    # Override methods
    ####################################################