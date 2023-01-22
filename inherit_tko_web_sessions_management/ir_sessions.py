# -*- encoding: utf-8 -*-

import os
from time import time

from odoo import api
from odoo import fields, models
from odoo.http import root
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ir_sessions(models.Model):
    _inherit = 'ir.sessions'
    _description = "Sessions"

    last_active_time = fields.Char(string='Last Page Browse')

    def validate_sessions(self):
        delay = self.env['ir.config_parameter']._auth_timeout_get_parameter_delay()
        sessions = self.sudo().search(['|', ('last_active_time', '<', time() - delay),
                                       ('date_expiration', '<=',
                                        fields.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                       ('logged_in', '=', True)])
        if sessions:
            sessions._close_session(logout_type='to')
        return True

    def delete_session(self):
        try:
            dir = os.path.join(root.session_store.path)
            files = "find %s -type f -exec rm -v {} \;" % dir
            if os.path.exists(dir):
                os.system(files)
        except OSError:
            pass

    @api.multi
    def _close_session(self, logout_type=None):
        redirect = False

        for r in self:
            if r.user_id.id == self.env.user.id:
                redirect = True
            session = root.session_store.get(r.session_id)
            try:
                session.logout(logout_type=logout_type, env=self.env)
                storename = 'werkzeug_%s.sess' % (r.session_id)
                path = os.path.join(root.session_store.path, storename)
                if os.path.exists(path):
                    os.unlink(path)
            except OSError:
                pass
        return redirect
