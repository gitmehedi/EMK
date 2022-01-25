from odoo import models, fields, api


class InheritedLetterCredit(models.Model):
    _inherit = 'letter.credit'

    @api.depends('state')
    def get_can_edit(self):
        amendment_context = self.env.context.get('is_amendment')
        flag = self.env.user.has_group('samuda_custom_letter_of_credit.group_commercial_adviser_export')

        if self.state:
            if flag and self.state == 'confirmed':
                self.can_edit = True
            elif flag and self.state == 'progress':
                self.can_edit = True
            elif self.state == 'draft':
                self.can_edit = True
            elif not flag and amendment_context:
                self.can_edit = True
        else:
            self.can_edit = True

    can_edit = fields.Boolean(string='Group User', compute='get_can_edit', store=False)
    is_amendment = fields.Boolean(string='Is Amendment', store=False)
