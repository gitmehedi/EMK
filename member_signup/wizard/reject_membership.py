from odoo import models, fields, api


class SetMembershipWizard(models.TransientModel):
    _name = 'reject.membership.wizard'

    reason = fields.Text(required=True, string='Rejection Reason')

    @api.multi
    def reject_membership(self):
        if self.reason:
            partner_ins = self.env['res.partner']
            member = partner_ins.browse(self._context['active_id'])
            member.write({'rejection_reason': self.reason, 'state': 'reject'})
            vals = {
                'template': 'member_signup.member_rejection_email_template',
                'email_to': member.email,
                'context': {'name': member.name, 'reason': self.reason},
            }
            member.mailsend(vals)

            return {
                'view_type': 'form',
                'view_mode': 'form',
                'src_model': 'res.partner',
                'res_model': 'res.partner',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': member.id
            }
