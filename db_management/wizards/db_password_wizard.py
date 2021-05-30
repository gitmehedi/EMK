from odoo import api, fields, models, tools, SUPERUSER_ID, _


class DBChangePasswordWizard(models.TransientModel):
    """ A wizard to manage the change of users' passwords. """
    _name = "db.change.password.wizard"
    _description = "Change Password Wizard"

    source_db_user = fields.Char(string='Source Username')
    source_db_pass = fields.Char(string='Source Password')
    dest_db_user = fields.Char(string='Dest. Usernamme')
    dest_db_pass = fields.Char(string='Dest. Password')

    def db_change_password(self):
        self.ensure_one()
        context = self._context
        db = self.env[context['active_model']].browse([context['active_id']])
        if db.location=='remote':
            if self.source_db_user:
                db.write({'source_db_user': self.source_db_user})
            if self.source_db_pass:
                db.write({'source_db_pass': self.source_db_pass})
            if self.dest_db_user:
                db.write({'dest_db_user': self.dest_db_user})
            if self.dest_db_pass:
                db.write({'dest_db_pass': self.dest_db_pass})

        return {'type': 'ir.actions.act_window_close'}
