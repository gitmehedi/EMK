from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
import datetime

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
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
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
    qty_available = fields.Float('In Stock', compute='_getProductQuentity', store=True)
    name = fields.Text('Specification', store=True)
    sequence = fields.Integer('Sequence')
