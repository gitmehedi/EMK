from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorAgreement(models.Model):
    _name = "agreement"
    _inherit = ["agreement",'mail.thread']


    agreement_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
    ], string='Type', required=True, default='purchase', invisible=True)

    code = fields.Char(required=False, copy=False)
    name = fields.Char(required=False,track_visibility='onchange')
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict', required=True,track_visibility='onchange',
        domain=[('parent_id', '=', False),('supplier','=',True)],readonly= True,states={'draft':[('readonly', False)]})
    product_id = fields.Many2one('product.product', string='Product', required=True, readonly= True,
                                 track_visibility='onchange',states={'draft':[('readonly', False)]})
    start_date = fields.Date(string='Start Date', required=True,readonly=True,track_visibility='onchange',
                             states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', required=True,readonly=True,track_visibility='onchange',
                           states={'draft': [('readonly', False)]})
    advance_amount = fields.Float(string="Advance Amount", readonly=1,track_visibility='onchange')
    adjusted_amount = fields.Float(string="Adjusted Amount", readonly=1,track_visibility='onchange')
    acc_move_line_ids = fields.One2many('account.move.line', 'agreement_id', readonly=True, copy=False,
                                        ondelete='restrict')
    description = fields.Text('Notes',readonly= True, track_visibility='onchange',
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

    @api.constrains('start_date','end_date')
    def check_end_date(self):
        date = fields.Date.today()
        if self.start_date < date:
            raise ValidationError("Agreement 'Start Date' never be less then 'Current Date'.")
        elif self.end_date < date:
            raise ValidationError("Agreement 'End Date' never be less then 'Current Date'.")
        elif self.start_date > self.end_date:
            raise ValidationError("Agreement 'End Date' never be less then 'Start Date'.")


    @api.one
    def action_payment(self):
        self.state = 'done'

    @api.one
    def action_confirm(self):
        self.state = 'confirm'

    @api.one
    def action_validate(self):
        self.state = 'done'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(VendorAgreement, self).unlink()

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
            'context': {'end_date': self.end_date or False},
        }
        return result

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    agreement_id = fields.Many2one('agreement')
