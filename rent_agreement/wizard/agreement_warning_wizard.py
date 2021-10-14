from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class AgreementWarning(models.TransientModel):
    _name = "agreement.warning.wizard"

    text = fields.Text(size=150)
    warning_type = fields.Selection([
        ('reject_amendment', "Reject Amendment"),
        ('reject_agreement', "Inactive Agreement")], string="Warning Type")

    def action_inactive(self):
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['vendor.advance'].browse(active_id)
        message = 'The following changes have been requested:' + '\n' + u'\u2022' + 'Status: Active' + u'\u2192' + 'Inactive'
        agreement.message_post(body=message)
        self.env['agreement.history'].create({
            'rent_id': active_id,
            'narration': message,
            'active_status': False
        })
        agreement.write({'is_amendment': True, 'maker_id': self.env.user.id})

    @api.multi
    def action_reject_amendment(self):
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['vendor.advance'].browse(active_id)
        if self.env.user.id == agreement.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if agreement.is_amendment:
            requested = agreement.history_line_ids.search([('state', '=', 'pending'),
                                                           ('rent_id', '=', agreement.id)], order='id desc', limit=1)
            requested.write({'state': 'reject'})
            agreement.write({
                'is_amendment': False,
                'approver_id': self.env.user.id
            })

    @api.multi
    def action_reject_agreement(self):
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['vendor.advance'].browse(active_id)
        message = "The following changes have been requested:\n" + u'\u2022' + ' Status: Active' + u'\u2192' + 'Reject'
        if not agreement.is_rejection:
            self.env['agreement.history'].create({
                'rent_id': active_id,
                'narration': message,
            })
            agreement.write({'is_rejection': True, 'maker_id': self.env.user.id})
