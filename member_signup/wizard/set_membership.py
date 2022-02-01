from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SetMembershipWizard(models.TransientModel):
    _name = 'set.membership.sequence.wizard'

    membership_seq = fields.Char(required=True, string='Membership ID')

    @api.multi
    def set_membership(self):
        if self.membership_seq:
            partner_ins = self.env['res.partner']
            seq = partner_ins.browse(self._context['active_id'])
            check_mem = partner_ins.search([('member_sequence', '=', self.membership_seq), ('id', '!=', seq.id)])
            if len(check_mem) > 0:
                raise ValidationError(_("Membership ID [{0}] should not duplicate".format(self.membership_seq)))
            else:
                seq.write({'member_sequence': self.membership_seq})
                vals = {
                    'template': 'member_signup.member_approval_email_template',
                    'email_to': seq.email,
                    'context': {'name': seq.name, 'membership_id': self.membership_seq},
                }
                seq.mailsend(vals)

            return {
                'view_type': 'form',
                'view_mode': 'form',
                'src_model': 'res.partner',
                'res_model': 'res.partner',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': seq.id
            }
