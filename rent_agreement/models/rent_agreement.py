from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorAdvance(models.Model):
    _name = "vendor.advance"
    _inherit = ['vendor.advance', 'mail.thread', 'ir.needaction_mixin']

    start_date = fields.Date(string='Start Date', default=fields.Date.context_today, readonly=True,
                             track_visibility='onchange', states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', readonly=True, track_visibility='onchange',
                           states={'draft': [('readonly', False)]})
    service_value = fields.Float(string="Service Value", required=True, readonly=True, default=0.0,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]},
                                 help="Service value.")
    rent_type = fields.Selection([('general', "General Rent"), ('govt_premise', "Govt. Premise Rent")],
                                 string="Rent Type", track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)]})
    area = fields.Float(string='Area (ft)', readonly=True, states={'draft': [('readonly', False)]})
    rate = fields.Float(string='Rate', readonly=True, states={'draft': [('readonly', False)]})
    additional_service = fields.Many2one('product.product', string='Additional Service',
                                         required=False, readonly=True, track_visibility='onchange',
                                         states={'draft': [('readonly', False)]}, help="Additional Service.")
    additional_service_value = fields.Float(string="Ad. Service Value", readonly=True, default=0.0,
                                            track_visibility='onchange', states={'draft': [('readonly', False)]},
                                            help="Additional Service value.")
    additional_advance_amount = fields.Float(string="Ad. Approved Advance", default=0.0, copy=False,
                                             track_visibility='onchange', help="Additional Advance Amount.")
    total_advance_amount = fields.Float(string="Total Approved Advance", readonly=True, copy=False,
                                        compute="_compute_total_advance_amount", store=True,
                                        track_visibility='onchange', help="Total Advance Amount.")
    total_service_value = fields.Float(string="Total Service Value", readonly=True, copy=False,
                                       compute="_compute_total_service_value", store=True,
                                       track_visibility='onchange', help="Total Service Value")
    billing_period = fields.Selection([('monthly', "Monthly"), ('yearly', "Yearly")],
                                      string="Billing Period", track_visibility='onchange', readonly=True,
                                      states={'draft': [('readonly', False)]})
    is_amendment = fields.Boolean(default=False, string="Is Amendment", copy=False,
                                  help="Take decision that, this agreement is amendment.")
    is_rejection = fields.Boolean(default=False, string="Is Rejection", copy=False)
    history_line_ids = fields.One2many('agreement.history', 'rent_id', readonly=True, copy=False,
                                       ondelete='restrict')
    adjustment_value = fields.Float(string="Adjustment Value", required=True, readonly=True, default=0.0,
                                    track_visibility='onchange', states={'draft': [('readonly', False)]},
                                    help="Adjustment amount which will be adjust in bill.")
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True, required=True,
                                        states={'draft': [('readonly', False)]})
    account_analytic_id = fields.Many2one('account.analytic.account', readonly=True,
                                          states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Waiting for Approval"),
        ('approve', 'Active'),
        ('done', "Closed"),
        ('cancel', "Canceled"),
        ('inactive', "Inactive"),
        ('expired', "Expired"),
        ('reject', "Rejected")], default='draft', string="Status",
        track_visibility='onchange', copy=False)
    move_count = fields.Char(compute='_count_move', store=True, string='No of Moves')

    @api.depends('move_ids')
    def _count_move(self):
        for record in self:
            record.move_count = len(record.move_ids)

    @api.one
    @api.depends('advance_amount', 'additional_advance_amount')
    def _compute_total_advance_amount(self):
        for record in self:
            record.total_advance_amount = record.advance_amount + record.additional_advance_amount

    @api.one
    @api.depends('service_value', 'additional_service_value')
    def _compute_total_service_value(self):
        for record in self:
            record.total_service_value = record.service_value + record.additional_service_value

    @api.one
    @api.depends('adjusted_amount', 'initial_outstanding_amount', 'state', 'total_advance_amount', 'type')
    def _compute_outstanding_amount(self):
        for va in self:
            if va.state not in ('draft', 'confirm', 'cancel'):
                if va.type == 'single':
                    va.outstanding_amount = va.initial_outstanding_amount - va.adjusted_amount
                else:
                    va.outstanding_amount = va.total_advance_amount - va.adjusted_amount
            else:
                va.outstanding_amount = 0.0

    # overwrite get_seq to generate sequence for rent agreement
    def get_seq(self):
        res = super(VendorAdvance, self).get_seq()
        if self.type == 'multi':
            rent_sequence = self.env['ir.sequence'].next_by_code('rent.agreement') or ''
            res = rent_sequence
        return res

    @api.multi
    @api.onchange('area', 'rate')
    def onchange_service_value(self):
        for rec in self:
            if rec.area and rec.rate:
                rec.service_value = rec.area * rec.rate

    # overwrite _compute_payable_to_supplier to calculate  payable if there is any amendment
    @api.one
    @api.depends('total_advance_amount', 'total_deduction', 'vat_id', 'tds_id', 'type', 'initial_outstanding_amount',
                 'security_deposit')
    def _compute_payable_to_supplier(self):
        for record in self:
            if record.type == 'single':
                payable_to_supplier = record.initial_outstanding_amount - record.total_deduction
                record.payable_to_supplier = payable_to_supplier
            else:
                record.payable_to_supplier = record.total_advance_amount

    @api.multi
    def action_amendment(self):
        if self.is_amendment:
            raise UserError(_('There is already pending amendment waiting for approval. '
                              'At first approve that !'))
        res = self.env.ref('rent_agreement.view_amendment_agreement_form_wizard')
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
                        'adjustment_value': self.adjustment_value or False,
                        'area': self.area or False,
                        'rate': self.rate or False,
                        'service_value': self.service_value or False,
                        'account_id': self.account_id.id or False
                        }
        }
        return result

    @api.multi
    def action_approve_amendment(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.is_amendment == True:
            requested = self.history_line_ids.search([('state', '=', 'pending'),
                                                      ('rent_id', '=', self.id)],
                                                     order='id desc', limit=1)
            if requested:
                self.write({
                    'end_date': requested.end_date,
                    'additional_advance_amount': self.additional_advance_amount + requested.advance_amount_add,
                    'adjustment_value': requested.adjustment_value,
                    'area': requested.area,
                    'rate': requested.rate,
                    'service_value': requested.service_value,
                    'account_id': requested.account_id.id,
                    'is_amendment': False,
                    'active': requested.active_status,
                    'state': 'inactive' if not requested.active_status else 'approve',
                    'approver_id': self.env.user.id,
                })
                amount = requested.advance_amount_add
                if amount > 0:
                    journal_type = self.env.ref('vendor_advance.vendor_advance_journal')
                    self.create_journal_for_amendment(amount, journal_type)
                requested.write({'state': 'confirm'})

    def create_journal_for_amendment(self, amount, journal_id):
        move_data = {}
        move_data['journal_id'] = journal_id.id
        move_data['date'] = fields.Date.today()
        move_data['state'] = 'draft'
        move_data['name'] = self.name
        move_data['partner_id'] = self.partner_id.id
        move_data['company_id'] = self.company_id.id
        move_data['advance_id'] = self.id
        move_line_data = []

        debit_line = self._get_debit_line_for_amendment(amount)
        move_line_data.append([0, 0, debit_line])

        credit_line = self._get_credit_line_for_amendment(amount)
        move_line_data.append([0, 0, credit_line])

        move_data['line_ids'] = move_line_data
        move = self.env['account.move'].create(move_data)
        move.sudo().post()
        return move

    def _get_debit_line_for_amendment(self, amount):
        debit_line = {
            'name': self.description or 'Rent',
            'ref': self.name,
            'date': fields.Date.today(),
            'account_id': self.account_id.id,
            'debit': amount,
            'credit': 0.0,
            'company_id': self.company_id.id,
            'analytic_account_id': self.account_analytic_id.id or False
        }
        return debit_line

    def _get_credit_line_for_amendment(self, amount):
        credit_line = {
            'name': self.description or 'Rent',
            'ref': self.name,
            'date': fields.Date.today(),
            'account_id': self.partner_id.property_account_payable_id.id,
            'debit': 0.0,
            'credit': amount,
            'company_id': self.company_id.id,
            'analytic_account_id': self.account_analytic_id.id or False
        }
        return credit_line

    @api.multi
    def action_reject_amendment(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        res = self.env.ref('rent_agreement.agreement_warning_wizard_view')
        return {
            'name': _('Warning'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'agreement.warning.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {
                'default_text': 'Are you sure to reject the amendment?',
                'default_warning_type': 'reject_amendment'
            }
        }

    @api.multi
    def action_inactive_agreement(self):
        res = self.env.ref('rent_agreement.agreement_warning_wizard_view')
        return {
            'name': _('Warning'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'agreement.warning.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'active_id': self.id,
            'context': {
                'default_text': 'Are you sure to inactive the agreement?' or False,
                'default_warning_type': 'inactive_agreement' or False
            }
        }

    @api.multi
    def action_reject_agreement(self):
        res = self.env.ref('rent_agreement.agreement_warning_wizard_view')
        warning = "The current Outstanding Advance Amount of this Agreement is {}.\n\nAre you sure to reject the agreement?".format(
            self.outstanding_amount)
        return {
            'name': _('Warning'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'agreement.warning.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'active_id': self.id,
            'context': {
                'default_text': warning or False,
                'default_warning_type': 'reject_agreement' or False
            }
        }

    @api.multi
    def action_approve_rejection(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.is_rejection:
            requested = self.history_line_ids.search([('state', '=', 'pending'),
                                                      ('rent_id', '=', self.id)], order='id desc', limit=1)
            if requested:
                self.write({'state': 'reject', 'is_rejection': False, 'approver_id': self.env.user.id})
                requested.write({'state': 'confirm'})

    @api.multi
    def action_cancel_rejection(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.is_rejection:
            requested = self.history_line_ids.search([('state', '=', 'pending'),
                                                      ('rent_id', '=', self.id)], order='id desc', limit=1)
            if requested:
                self.write({'is_rejection': False, 'approver_id': self.env.user.id})
                requested.write({'state': 'reject'})

    @api.multi
    def action_active(self):
        if self.state in ('expired',):
            self.state = 'approve'

    @api.constrains('adjustment_value', 'service_value', 'advance_amount', 'additional_service_value', 'type', 'area',
                    'rate')
    def check_amount(self):
        if self.type == 'multi':
            if self.adjustment_value < 0:
                raise ValidationError(
                    "Please Check Your Adjustment Value!! \n Amount Never Take Negative Value!")
            elif self.service_value < 0:
                raise ValidationError(
                    "Please Check Your Service Value!! \n Amount must not be less than 0.0")
            elif self.additional_service_value < 0:
                raise ValidationError(
                    "Please Check Your Additional Service Value!! \n Amount Never Take Negative Value!")
            elif self.area < 0:
                raise ValidationError("Please Check Area!! \n It Never Take Negative Value!")
            elif self.rate < 0:
                raise ValidationError("Please Check Rate!! \n It Never Take Negative Value!")
            if self.adjustment_value > self.total_advance_amount:
                raise ValidationError(
                    "Adjustment Value should not be greater than Approved Advance.")
            if self.adjustment_value > self.total_service_value:
                raise ValidationError('Adjustment Value must not greater than Total Service value')

    @api.constrains('end_date', 'type')
    def _check_end_date(self):
        if self.type == 'multi':
            if self.end_date:
                if self.end_date < fields.Date.today():
                    raise ValidationError("Expire Date can not be less than the Current day")

    def get_debit_item_data(self, journal_id):
        res = super(VendorAdvance, self).get_debit_item_data(journal_id)
        if res:
            if self.type == 'multi':
                res['name'] = self.description or 'Rent'
                res['analytic_account_id'] = self.account_analytic_id.id or False
        return res

    def get_supplier_credit_item_data(self, journal_id, supplier_credit_amount):
        res = super(VendorAdvance, self).get_supplier_credit_item_data(journal_id, supplier_credit_amount)
        if res:
            if self.type == 'multi':
                res['name'] = self.description or 'Rent'
        return res

    def action_expire_agreement(self):
        current_date = fields.date.today()
        obj = self.env['vendor.advance'].search([('type', '=', 'multi'),
                                                 ('end_date', '<', current_date),
                                                 ('state', '=', 'approve')])
        for rent in obj:
            rent.write({'state': 'expired'})

    @api.multi
    def open_entries(self):
        move_ids = []
        for ra in self:
            for move in ra.move_ids:
                move_ids.append(move.id)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }


class AgreementHistory(models.Model):
    _name = "agreement.history"
    _order = 'id desc'

    name = fields.Char(string='Name', readonly=True)
    end_date = fields.Date(string='Expire Date', readonly=True)
    advance_amount_add = fields.Float(string="Advance Amount Addition", readonly=True)
    adjustment_value = fields.Float(string="Adjustment Value", readonly=True)
    area = fields.Float(string='Area (ft)', readonly=True)
    rate = fields.Float(string='Rate', readonly=True)
    service_value = fields.Float(string="Service Value", readonly=True)
    account_id = fields.Many2one('account.account', string="Agreement Account", readonly=True)
    rent_id = fields.Many2one('vendor.advance', string="Rent", readonly=True)
    state = fields.Selection([
        ('pending', "Pending"),
        ('confirm', "Approved"),
        ('reject', "Rejected")], default='pending', string="Status")
    narration = fields.Text('Amendment Request', readonly=True)
    active_status = fields.Boolean('Status', readonly=True)
