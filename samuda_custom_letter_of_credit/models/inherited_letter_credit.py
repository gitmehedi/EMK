from odoo import models, fields, api


class InheritedLetterCredit(models.Model):
    _inherit = 'letter.credit'

    @api.depends('state')
    def get_can_edit(self):
        flag = self.env.user.has_group('samuda_custom_letter_of_credit.group_commercial_adviser_export')
        if self.state:
            if flag and self.state == 'confirmed':
                self.can_edit = True
            elif flag and self.state == 'progress':
                self.can_edit = True
            elif self.state == 'draft':
                self.can_edit = True
            elif self.state == 'amendment':
                self.can_edit = True
        else:
            self.can_edit = True

    can_edit = fields.Boolean(string='Group User', compute='get_can_edit')
