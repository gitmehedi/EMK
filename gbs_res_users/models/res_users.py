from odoo import fields, models, api
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def unlink(self):
        for a in self:
            query = """ select id from mail_message where create_uid=%s or write_uid=%s """ % (a.id, a.id)
            self._cr.execute(query)
            results = self._cr.fetchone()
            if results:
                raise UserError(
                    "Unable to delete the user!!")

        return super(ResUsers, self).unlink()