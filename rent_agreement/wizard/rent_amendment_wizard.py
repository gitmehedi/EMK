from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError


class AmendmentAgreementWizard(models.TransientModel):
    _name = 'amendment.agreement.wizard'

    def _get_default_status(self):
        rent = self.env['vendor.advance'].browse(self._context['active_id'])
        if rent.active:
            status = 'active'
        else:
            status = 'inactive'
        return status

    name = fields.Char('Name', readonly=True)
    change_date = fields.Boolean('Change Expire Date', default=False)
    end_date = fields.Date(string='Expire Date', default=lambda self: self.env.context.get('end_date'))
    advance_amount_add = fields.Float(string="Advance Amount Addition")
    change_adjustment_value = fields.Boolean('Change Adjustment Value', default=False)
    adjustment_value = fields.Float(string="Adjustment Value", required=True,
                                    default=lambda self: self.env.context.get('adjustment_value'))
    change_service_value = fields.Boolean('Change Service Value', default=False)
    service_value = fields.Float(string="Service Value", required=True,
                                 default=lambda self: self.env.context.get('service_value'))
    area = fields.Float(string='Area (ft)', default=lambda self: self.env.context.get('area'))
    rate = fields.Float(string='Rate', default=lambda self: self.env.context.get('rate'))
    account_id = fields.Many2one('account.account', string="Agreement Account", required=True,
                                 default=lambda self: self.env.context.get('account_id'))
    change_status = fields.Boolean('Change Status', default=False)
    status = fields.Selection(
        [('active', "Active"),
         ('inactive', "Inactive")], default=_get_default_status, string='Status')

    @api.multi
    def generate(self):
        rent = self.env['vendor.advance'].browse(self._context['active_id'])
        if rent.is_amendment:
            raise UserError(_('There is already pending amendment waiting for approval. '
                              'At first approve that !'))
        message = 'The following changes have been requested:'
        if self.end_date != rent.end_date:
            message += '\n' + u'\u2022' + ' Expire Date: ' + str(rent.end_date) + u'\u2192' + str(self.end_date)
        if self.adjustment_value != rent.adjustment_value:
            message += '\n' + u'\u2022' + ' Adjustment Value: ' + str(rent.adjustment_value) + u'\u2192' + str(self.adjustment_value)
        if self.service_value != rent.service_value:
            message += '\n' + u'\u2022' + ' Service Value: ' + str(rent.service_value) + u'\u2192' + str(self.service_value)
        if self.advance_amount_add > 0:
            message += '\n' + u'\u2022' + ' Advance Amount Addition: ' + str(self.advance_amount_add)
        active_status = True if self.status == 'active' else False
        if rent.active != active_status:
            if self.status == 'active':
                message += '\n' + u'\u2022' + ' Status: Inactive' + u'\u2192' + 'Active'
            else:
                message += '\n' + u'\u2022' + ' Status: Active' + u'\u2192' + 'Inactive'
        rent.message_post(body=message)
        history = self.env['agreement.history'].create({
            'end_date': self.end_date,
            'advance_amount_add': self.advance_amount_add,
            'adjustment_value': self.adjustment_value,
            'area': self.area,
            'rate': self.rate,
            'service_value': self.service_value,
            'account_id': self.account_id.id,
            'rent_id': self._context['active_id'],
            'narration': message,
            'active_status': active_status
        })
        rent.write({'is_amendment': True, 'maker_id': self.env.user.id})
        return history

    @api.constrains('end_date')
    def check_end_date(self):
        date = fields.Date.today()
        if self.end_date:
            if self.end_date < date:
                raise ValidationError("Agreement 'Expire Date' never be less than 'Current Date'.\n"
                                      "Please change the expire date to greater than previous day.")

    @api.constrains('advance_amount_add','adjustment_value','service_value')
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

    @api.onchange('area', 'rate')
    def _onchange_service_value(self):
        if self.area and self.rate:
            self.service_value = self.area * self.rate

    @api.constrains('end_date', 'advance_amount_add', 'adjustment_value', 'service_value', 'status')
    def check_amendment(self):
        rent = self.env['vendor.advance'].browse(self._context['active_id'])
        active_status = True if self.status == 'active' else False
        if self.end_date == rent.end_date and self.adjustment_value == rent.adjustment_value and\
                self.service_value == rent.service_value and self.advance_amount_add == 0 and active_status == rent.active:
            raise ValidationError("No changes have been requested")

    @api.constrains('service_value')
    def check_service_value(self):
        if self.change_service_value:
            service_value = self.area * self.rate
