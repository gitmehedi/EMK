from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorAgreement(models.Model):
    _name = "agreement"
    _order = 'name desc'
    _inherit = ["agreement", 'mail.thread', 'ir.needaction_mixin']

    code = fields.Char(required=False, copy=False)
    name = fields.Char(required=False, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', required=True,
                                 track_visibility='onchange',
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)], readonly=True,
                                 states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', string='Service', required=True, readonly=True,
                                 domain=[('type', '=', 'service')], track_visibility='onchange',
                                 states={'draft': [('readonly', False)]},
                                 help="Agreement Service.")
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today, required=True, readonly=True,
                             track_visibility='onchange', states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', required=True, readonly=True, track_visibility='onchange',
                           states={'draft': [('readonly', False)]})
    pro_advance_amount = fields.Float(string="Proposed Amount", required=True, readonly=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]},
                                      help="Proposed advance amount. Initially proposed amount raise by vendor.")
    adjustment_value = fields.Float(string="Adjustment Value", required=True, readonly=True,
                                    track_visibility='onchange', states={'draft': [('readonly', False)]},
                                    help="Adjustment amount which will be adjust in bill.")
    service_value = fields.Float(string="Service Value", required=True, readonly=True,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]},
                                 help="Service value.")
    advance_amount = fields.Float(string="Approved Advance", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  track_visibility='onchange', help="Finally granted advance amount.")
    adjusted_amount = fields.Float(string="Adjusted Amount", track_visibility='onchange',
                                   help="Total amount which are already adjusted in bill.")
    outstanding_amount = fields.Float(string="Outstanding Amount", compute='_compute_outstanding_amount', readonly=True,
                                      track_visibility='onchange', help="Remaining Amount to adjustment.")
    account_id = fields.Many2one('account.account', string="Agreement Account", required=True, readonly=True,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]},
                                 help="Account for the agreement.")
    acc_move_line_ids = fields.One2many('account.move.line', 'agreement_id', readonly=True, copy=False,
                                        ondelete='restrict')
    description = fields.Text('Notes', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    company_id = fields.Many2one('res.company', string='Company', readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('agreement'))
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('done', "Done"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')

    agreement_type = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ], string='Type', required=True,
                                      default='purchase', invisible=True)
    is_remaining = fields.Boolean(compute='_compute_is_remaining', default=True, store=True, string="Is Remaining",
                                  help="Take decision that advance amount is remaing or not")
    is_amendment = fields.Boolean(default=False, string="Is Amendment",
                                  help="Take decision that, this agreement is amendment.")

    payment_line_ids = fields.One2many('payment.instruction', 'agreement_id', readonly=True, copy=False)
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)
    total_payment_approved = fields.Float('Advance Paid', compute='_compute_payment_amount',
                                          store=True, readonly=True, track_visibility='onchange', copy=False)
    active = fields.Boolean(track_visibility='onchange')
    history_line_ids = fields.One2many('agreement.history', 'agreement_id', readonly=True, copy=False,
                                       ondelete='restrict')
    operating_unit_id = fields.Many2one('operating.unit', 'Branch',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True, required=True,
                                        states={'draft': [('readonly', False)]})

    @api.one
    @api.depends('payment_line_ids.amount', 'payment_line_ids.state')
    def _compute_payment_amount(self):
        for va in self:
            va.total_payment_amount = sum(line.amount for line in va.payment_line_ids if line.state not in ['cancel'])
            va.total_payment_approved = sum(
                line.amount for line in va.payment_line_ids if line.state in ['approved'])

    @api.one
    @api.depends('adjusted_amount', 'total_payment_approved')
    def _compute_outstanding_amount(self):
        for va in self:
            va.outstanding_amount = va.total_payment_approved - va.adjusted_amount

    @api.depends('adjusted_amount', 'advance_amount')
    def _compute_is_remaining(self):
        for record in self:
            if record.adjusted_amount and record.advance_amount and record.adjusted_amount >= record.advance_amount:
                record.is_remaining = False
            else:
                record.is_remaining = True

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('name')
        vals['name'] = seq

        return super(VendorAgreement, self).create(vals)

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        date = fields.Date.today()
        # if not self.is_amendment and self.start_date < date:
        #     raise ValidationError("Agreement 'Start Date' never be less than 'Current Date'.")
        if self.end_date < date:
            raise ValidationError("Agreement 'End Date' never be less than 'Current Date'.")
        elif self.start_date >= self.end_date:
            raise ValidationError("Agreement 'End Date' never be less than or equal to 'Start Date'.")

    @api.constrains('pro_advance_amount', 'adjustment_value', 'service_value')
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

    @api.multi
    def action_payment(self):
        if self.advance_amount <= self.total_payment_amount:
            raise ValidationError(_('No payment instruction needed!'))

        res = self.env.ref('vendor_agreement.view_agreement_payment_instruction_wizard')

        return {
            'name': _('Payment Instruction'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'agreement.payment.instruction.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'amount': self.advance_amount - self.total_payment_amount or 0.0,
                        'advance_amount': self.advance_amount or 0.0,
                        'total_payment_approved': self.total_payment_approved or 0.0,
                        'currency_id': self.env.user.company_id.currency_id.id or False,
                        'operating_unit_id': self.operating_unit_id.id or False,
                        },
        }

    @api.one
    def action_confirm(self):
        self.state = 'confirm'

    @api.one
    def action_validate(self):
        self.state = 'done'

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(VendorAgreement, self).unlink()

    @api.multi
    def action_amendment(self):
        if self.is_amendment == True:
            raise UserError(_('There is already pending amendment waiting for approval. '
                              'At first approve that !'))
        res = self.env.ref('vendor_agreement.view_amendment_agreement_form_wizard')
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

    @api.multi
    def action_approve_amendment(self):
        if self.is_amendment == True:
            requested = self.history_line_ids.search([('state', '=', 'pending'),
                                                      ('agreement_id', '=', self.id)],
                                                     order='id desc', limit=1)
            if requested:
                self.write({
                    'end_date': requested.end_date,
                    'advance_amount': self.advance_amount + requested.advance_amount_add,
                    'adjustment_value': requested.adjustment_value,
                    'service_value': requested.service_value,
                    'account_id': requested.account_id.id,
                    'is_amendment': False,
                })
                requested.write({'state': 'confirm'})

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]

    def name_get(self):
        res = []
        for agr in self:
            name = agr.name
            if agr.product_id:
                name = u'%s[%s]' % (agr.name,agr.product_id.name)
            res.append((agr.id, name))
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    agreement_id = fields.Many2one('agreement', copy=False)


class VendorAgreementHistory(models.Model):
    _name = "agreement.history"
    _order = 'id desc'

    name = fields.Char(string='Name', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)
    advance_amount_add = fields.Float(string="Advance Amount Addition", readonly=True)
    adjustment_value = fields.Float(string="Adjustment Value", readonly=True)
    service_value = fields.Float(string="Service Value", readonly=True)
    account_id = fields.Many2one('account.account', string="Agreement Account", readonly=True)
    agreement_id = fields.Many2one('agreement', string="Agreement Id", readonly=True)
    state = fields.Selection([
        ('pending', "Pending"),
        ('confirm', "Confirmed")], default='pending', string="Status")
