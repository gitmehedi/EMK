from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InheritedLetterCredit(models.Model):
    _inherit = "letter.credit"

    @api.constrains('title')
    @api.one
    def _check_title(self):
        if len(self.title) > 16:
            raise ValidationError('Description must not exceed 16 characters!')


class InheritedLcNumberWizard(models.TransientModel):
    _inherit = "lc.number.wizard"

    @api.multi
    def save_number(self):
        analytic_account_obj = self.env['account.analytic.account']
        analytic_account_name = ''
        form_id = self.env.context.get('active_id')
        lc_form_obj = self.env['letter.credit'].search([('id', '=', form_id)])
        if lc_form_obj.pi_ids_temp:
            company_id = lc_form_obj.pi_ids_temp[0].suspend_security().operating_unit_id.company_id.id
            analytic_account_name = 'LC : ' + self.name + '-' + lc_form_obj.title + '-' + lc_form_obj.pi_ids_temp[
                0].suspend_security().operating_unit_id.name
            analytic_account = analytic_account_obj.suspend_security().create(
                {'name': analytic_account_name, 'type': 'cost', 'company_id': company_id})
        else:
            analytic_account_name = 'LC : ' + self.name + '-' + lc_form_obj.title + '-' + lc_form_obj.operating_unit_id.name
            analytic_account = analytic_account_obj.suspend_security().create(
                {'name': analytic_account_name, 'type': 'cost',
                 'company_id': lc_form_obj.operating_unit_id.company_id.id})

        lc_form_obj.write(
            {'analytic_account_id': analytic_account.id})

        return super(InheritedLcNumberWizard, self).save_number()
