from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorAgreement(models.Model):
    _name = "agreement"
    _inherit = ["agreement", 'mail.thread']

    agreement_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
    ], string='Type', required=True, default='purchase', invisible=True)

    code = fields.Char(required=False, copy=False)
    name = fields.Char(required=False, track_visibility='onchange')
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict', required=True, track_visibility='onchange',
        domain=[('parent_id', '=', False), ('supplier', '=', True)], readonly=True,
        states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', string='Product/Service', required=True, readonly=True,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]})
    start_date = fields.Date(string='Start Date', default=fields.Date.today(), required=True, readonly=True,
                             track_visibility='onchange',
                             states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', required=True, readonly=True, track_visibility='onchange',
                           default=fields.Date.today(), states={'draft': [('readonly', False)]})
    pro_advance_amount = fields.Float(string="Proposed Advance Amount", required=True, readonly=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]})
    adjustment_value = fields.Float(string="Adjustment Value", required=True, readonly=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]})
    service_value = fields.Float(string="Service Value", required=True, readonly=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]})
    advance_amount = fields.Float(string="Advance Amount", readonly=1, track_visibility='onchange')
    adjusted_amount = fields.Float(string="Adjusted Amount", readonly=1, track_visibility='onchange')
    account_id = fields.Many2one('account.account', string="Agreement Account", required=True, readonly=True,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]})
    acc_move_line_ids = fields.One2many('account.move.line', 'agreement_id', readonly=True, copy=False,
                                        ondelete='restrict')
    description = fields.Text('Notes', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True,track_visibility='onchange',
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'agreement'))

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
        ('done', "Done"),
    ], default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('name')
        vals['name'] = seq

        return super(VendorAgreement, self).create(vals)

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        date = fields.Date.today()
        if self.start_date < date:
            raise ValidationError("Agreement 'Start Date' never be less then 'Current Date'.")
        elif self.end_date < date:
            raise ValidationError("Agreement 'End Date' never be less then 'Current Date'.")
        elif self.start_date >= self.end_date:
            raise ValidationError("Agreement 'End Date' never be less then 'Start Date'.")

    @api.constrains('pro_advance_amount','adjustment_value','service_value')
    def check_pro_advance_amount(self):
        if self.pro_advance_amount or self.adjustment_value or self.service_value:
            if self.pro_advance_amount < 0:
                raise ValidationError(
                    "Please Check Your Proposed Advance Amount!! \n Amount Never Take Negative Value!")
            elif self.adjustment_value < 0:
                raise ValidationError(
                    "Please Check Your Adjustment Value!! \n Amount Never Take Negative Value!")
            elif self.service_value < 0:
                raise ValidationError(
                    "Please Check Your Service Value!! \n Amount Never Take Negative Value!")



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
            'res_model': 'amendment.agreement.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'end_date': self.end_date or False,
                        'pro_advance_amount': self.pro_advance_amount or False,
                        'adjustment_value': self.adjustment_value or False,
                        'service_value': self.service_value or False,
                        'account_id': self.account_id.id or False
                        }
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
