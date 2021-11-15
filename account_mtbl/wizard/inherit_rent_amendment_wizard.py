from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AmendmentAgreementWizard(models.TransientModel):
    _inherit = 'amendment.agreement.wizard'

    def _get_default_status(self):
        rent = self.env['vendor.advance'].browse(self._context['active_id'])
        if rent.active:
            status = 'active'
        else:
            status = 'inactive'
        return status

    def _def_val(self, name):
        if 'active_id' in self._context:
            rent = self.env['vendor.advance'].browse(self._context['active_id'])
            return rent[name]

    vat_id = fields.Many2one('account.tax', string='VAT', domain=[('is_vat', '=', True)],
                             default=lambda self: self._def_val('vat_id'))
    tds_id = fields.Many2one('account.tax', string='TDS', domain=[('is_tds', '=', True)],
                             default=lambda self: self._def_val('tds_id'))
    payment_type = fields.Selection([('casa', 'CASA'), ('credit', 'Credit Account')], string='Payment To',
                                    default=lambda self: self._def_val('payment_type'))
    vendor_bank_acc = fields.Char(string='Vendor Bank Account', size=13, track_visibility='onchange',
                                  default=lambda self: self._def_val('vendor_bank_acc'))
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        default=lambda self: self._def_val('credit_account_id'))
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit Sequence',
                                                   default=lambda self: self._def_val('credit_sub_operating_unit_id'))
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch',
                                               default=lambda self: self._def_val('credit_operating_unit_id'))
    credit_operating_unit_domain_ids = fields.Many2many('operating.unit', readonly=True, store=False,
                                                        compute="_compute_credit_operating_unit_domain_ids")
    date = fields.Date(string='Date')
    additional_service_value = fields.Float(string="Ad. Service Value",
                                            default=lambda self: self._def_val('additional_service_value'))
    service_value = fields.Float(default=lambda self: self._def_val('service_value'))
    billing_period = fields.Selection([('monthly', "Monthly"), ('yearly', "Yearly")],
                                      string="Billing Period", default=lambda self: self._def_val('billing_period'))

    @api.multi
    def generate(self):
        rent = self.env['vendor.advance'].browse(self._context['active_id'])
        if rent.is_amendment:
            raise UserError(_('There is already pending amendment waiting for approval. '
                              'At first approve that !'))
        message = 'The following changes have been requested:'
        history = {}
        if self.end_date != rent.end_date:
            message += '\n' + u'\u2022' + ' Expire Date: ' + str(rent.end_date) + u'\u2192' + str(self.end_date)
            history['end_date'] = self.end_date
        if self.adjustment_value != rent.adjustment_value:
            message += '\n' + u'\u2022' + ' Adjustment Value: ' + str(rent.adjustment_value) + u'\u2192' + str(
                self.adjustment_value)
            history['adjustment_value'] = self.adjustment_value
        if self.service_value != rent.service_value:
            message += '\n' + u'\u2022' + ' Service Value: ' + str(rent.service_value) + u'\u2192' + str(
                self.service_value)
            history['service_value'] = self.service_value
        if self.advance_amount_add > 0:
            message += '\n' + u'\u2022' + ' Advance Amount Addition: ' + str(self.advance_amount_add)
            history['advance_amount_add'] = self.advance_amount_add
        if self.area != rent.area:
            message += '\n' + u'\u2022' + ' Area (ft): ' + str(self.area)
            history['area'] = self.area
        if self.rate != rent.rate:
            message += '\n' + u'\u2022' + ' Rate: ' + str(self.rate)
            history['rate'] = self.rate
        if self.vat_id != rent.vat_id:
            message += '\n' + u'\u2022' + ' VAT: ' + str(self.vat_id.name)
            history['vat_id'] = self.vat_id.id
        if self.tds_id != rent.tds_id:
            message += '\n' + u'\u2022' + ' TDS: ' + str(self.tds_id.name)
            history['tds_id'] = self.tds_id.id
        if self.payment_type != rent.payment_type:
            message += '\n' + u'\u2022' + ' Payment Type: ' + str(self.payment_type)
            history['payment_type'] = self.payment_type
        if self.vendor_bank_acc != rent.vendor_bank_acc:
            message += '\n' + u'\u2022' + ' Vendor Bank Account: ' + str(self.vendor_bank_acc)
            history['vendor_bank_acc'] = self.vendor_bank_acc
        if self.credit_account_id != rent.credit_account_id:
            message += '\n' + u'\u2022' + ' Credit Account: ' + str(self.credit_account_id.name)
            history['credit_account_id'] = self.credit_account_id.id
        if self.credit_sub_operating_unit_id != rent.credit_sub_operating_unit_id:
            message += '\n' + u'\u2022' + ' Credit Sequence: ' + str(self.credit_sub_operating_unit_id.name)
            history['credit_sub_operating_unit_id'] = self.credit_sub_operating_unit_id.id
        if self.credit_operating_unit_id != rent.credit_operating_unit_id:
            message += '\n' + u'\u2022' + ' Credit Branch: ' + str(self.credit_operating_unit_id.name)
            history['credit_operating_unit_id'] = self.credit_operating_unit_id.id
        if self.additional_service_value != rent.additional_service_value:
            message += '\n' + u'\u2022' + ' Ad. Service Value: ' + str(self.additional_service_value)
            history['additional_service_value'] = self.additional_service_value
        if self.billing_period != rent.billing_period:
            message += '\n' + u'\u2022' + ' Billing Period: ' + str(self.billing_period)
            history['billing_period'] = self.billing_period

        active_status = True if self.status == 'active' else False
        if rent.active != active_status:
            if self.status == 'active':
                message += '\n' + u'\u2022' + ' Status: Inactive' + u'\u2192' + 'Active'
            else:
                message += '\n' + u'\u2022' + ' Status: Active' + u'\u2192' + 'Inactive'

        rent.message_post(body=message)
        rent_history = super(AmendmentAgreementWizard, self).generate()
        history['rent_id'] = self._context['active_id']
        history['narration'] = message
        history['active_status'] = active_status

        return rent_history.write(history)

    @api.multi
    @api.depends('credit_sub_operating_unit_id')
    def _compute_credit_operating_unit_domain_ids(self):
        for rec in self:
            if rec.credit_sub_operating_unit_id.all_branch:
                rec.credit_operating_unit_domain_ids = self.env['operating.unit'].search([])
            else:
                rec.credit_operating_unit_domain_ids = rec.credit_sub_operating_unit_id.branch_ids

    @api.constrains('end_date')
    def check_end_date(self):
        date = fields.Date.today()
        if self.end_date:
            if self.end_date < date:
                raise ValidationError("Agreement 'Expire Date' never be less than 'Current Date'.\n"
                                      "Please change the expire date to greater than previous day.")

    @api.constrains('advance_amount_add', 'adjustment_value', 'service_value')
    def check_constrains_amount(self):
        if self.advance_amount_add or self.adjustment_value or self.service_value:
            if self.advance_amount_add < 0:
                raise ValidationError(
                    "Please Check Your Advance Amount Addition!! \n Amount Never Take Negative Value!")
            elif self.adjustment_value < 0:
                raise ValidationError(
                    "Please Check Your Adjustment Value!! \n Amount Never Take Negative Value!")
            elif self.service_value < 0:
                raise ValidationError(
                    "Please Check Your Service Value!! \n Amount Never Take Negative Value!")

    @api.onchange('change_date')
    def _onchange_change_date(self):
        for rec in self:
            default_end_date = self.env.context.get('end_date')
            if not rec.change_date:
                rec.end_date = default_end_date

    @api.onchange('change_adjustment_value')
    def _onchange_change_adjustment_value(self):
        for rec in self:
            default_adjustment_value = self.env.context.get('adjustment_value')
            if not rec.change_adjustment_value:
                rec.adjustment_value = default_adjustment_value

    @api.onchange('change_service_value')
    def _onchange_change_service_value(self):
        if not self.change_service_value:
            self.area = self.env.context.get('area')
            self.rate = self.env.context.get('rate')
            self.service_value = self.env.context.get('service_value')
        else:
            self.service_value = self.env.context.get('service_value')

    @api.onchange('area', 'rate')
    def _onchange_service_value(self):
        if self.change_service_value:
            self.service_value = self.area * self.rate

    @api.constrains('end_date', 'advance_amount_add', 'adjustment_value', 'service_value', 'status')
    def check_amendment(self):
        pass

    @api.constrains('service_value')
    def check_service_value(self):
        if self.change_service_value:
            service_value = self.area * self.rate
