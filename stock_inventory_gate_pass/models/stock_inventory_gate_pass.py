from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class StockInventoryGatePass(models.Model):
    _name = 'stock.inventory.gate.pass'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Gate Pass"
    _order = "id desc"

    name = fields.Char('ID#', size=30, readonly=True, track_visibility="onchange")
    request_date = fields.Date('Request Date', readonly=True,
                               default=fields.Date.today,
                               states={'draft': [('readonly', False)]}, track_visibility="onchange")
    request_id = fields.Many2one('res.users', string='Request User', required=True, readonly=True,
                                 default=lambda self: self.env.user,
                                 states={'draft': [('readonly', False)]}, track_visibility="onchange")
    approve_date = fields.Datetime('Approve Date', readonly=True,
                                   states={'draft': [('readonly', False)]}, track_visibility="onchange")
    approver_id = fields.Many2one('res.users', string='Request User', readonly=True,
                                  states={'draft': [('readonly', False)]}, track_visibility="onchange")
    description = fields.Text('Additional Information', readonly=True,
                              states={'draft': [('readonly', False)]}, track_visibility="onchange")
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True,
                                 track_visibility="onchange")
    active = fields.Boolean('Active', default=True, track_visibility="onchange")
    line_ids = fields.One2many('stock.inventory.gate.pass.line', 'line_id', readonly=True,
                               states={'draft': [('readonly', False)]},
                               track_visibility="onchange")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected'),
                              ], string='State', track_visibility='onchange', default='draft')

    @api.multi
    def act_draft(self):
        if self.state == 'confirm':
            self.state = 'draft'

    @api.multi
    def act_confirm(self):
        if self.state == 'draft':
            self.write({
                'state': 'confirm',
                'request_id': self.env.user.id,
                'request_date': fields.Date.today(),
            })

    @api.multi
    def act_approve(self):
        if self.state == 'confirm':
            sequence = self.env['ir.sequence'].sudo().next_by_code('stock.inventory.gate.pass')
            self.write({
                'name': sequence,
                'state': 'approve',
                'approver_id': self.env.user.id,
                'approve_date': fields.Date.today(),
            })

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft', 'confirm', 'approve'])]

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete this indent'))

        return super(StockInventoryGatePass, self).unlink()


class StockInventoryGatePassLine(models.Model):
    _name = 'stock.inventory.gate.pass.line'
    _description = 'Stock Inventory Gate Pass Line'

    line_id = fields.Many2one('stock.inventory.gate.pass', string='Line', required=True, ondelete='cascade',
                              track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product', required=True, track_visibility='onchange')
    model = fields.Char(string='Model Name', track_visibility='onchange')
    serial_no = fields.Char(string='Serial No', track_visibility='onchange')
    quantity = fields.Float('Quantity', required=True, digits=dp.get_precision('Product UoS'),
                            track_visibility='onchange')
    product_uom = fields.Many2one(related='product_id.uom_id', comodel='product.uom', string='Unit of Measure',
                                  store=True, track_visibility='onchange')
