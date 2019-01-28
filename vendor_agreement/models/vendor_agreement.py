from odoo import api, fields, models, _


class VendorAgreement(models.Model):
    _inherit = "agreement"

    agreement_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
    ], string='Type', required=True, default='purchase', invisible=True)

    code = fields.Char(required=False, copy=False)
    name = fields.Char(required=False)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict', required=True,
        domain=[('parent_id', '=', False)],readonly= True,states={'draft':[('readonly', False)]})
    product_id = fields.Many2one('product.product', string='Product', required=True, readonly= True,
                                 states={'draft':[('readonly', False)]})
    start_date = fields.Date(string='Start Date', required=True,readonly=True,
                             states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', required=True,readonly=True,
                           states={'draft': [('readonly', False)]})
    advance_amount = fields.Float(string="Advance Amount", readonly=1)
    adjusted_amount = fields.Float(string="Adjusted Amount", readonly=1)
    acc_move_line_ids = fields.One2many('account.move.line', 'agreement_id', readonly=True, copy=False,
                                        ondelete='restrict')
    description = fields.Text('Notes',readonly= True,
                                 states={'draft':[('readonly', False)]})

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
        ('done', "Done"),
    ], default='draft')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('name')
        vals['name'] = seq

        return super(VendorAgreement, self).create(vals)

    @api.one
    def action_confirm(self):
        self.state = 'confirm'

    @api.one
    def action_validate(self):
        self.state = 'done'

    @api.multi
    def action_amendment(self):
        res = self.env.ref('vendor_agreement.view_agreement_form_wizard')
        result = {
            'name': _('Agreement'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'agreement.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'partner_id': self.partner_id.id or False,
                        'product_id': self.product_id.id or False,
                        'start_date': self.start_date or False,
                        'end_date': self.end_date or False,
                        'advance_amount': self.advance_amount or False,
                        'adjusted_amount': self.adjusted_amount or False,
                        },
        }
        return result


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    agreement_id = fields.Many2one('agreement')
