# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from time import time

from odoo import api, http, models, tools, fields, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_cr_context
    def _auth_timeout_get_ignored_urls(self):
        """Pluggable method for calculating ignored urls
        Defaults to stored config param
        """
        params = self.env['ir.config_parameter']
        return params._auth_timeout_get_parameter_ignored_urls()

    @api.model_cr_context
    def _auth_timeout_deadline_calculate(self):
        """Pluggable method for calculating timeout deadline
        Defaults to current time minus delay using delay stored as config
        param.
        """
        params = self.env['ir.config_parameter']
        delay = params._auth_timeout_get_parameter_delay()
        if delay <= 0:
            return False
        return time() - delay

    @api.model_cr_context
    def _auth_timeout_session_terminate(self, session):
        """Pluggable method for terminating a timed-out session

        This is a late stage where a session timeout can be aborted.
        Useful if you want to do some heavy checking, as it won't be
        called unless the session inactivity deadline has been reached.

        Return:
            True: session terminated
            False: session timeout cancelled
        """
        if session.db and session.uid:
            session.logout(keep_db=True)
        return True

    @api.model_cr_context
    def _auth_timeout_check(self):
        """Perform session timeout validation and expire if needed."""

        if not http.request:
            return
        self.env['ir.sessions'].write({'last_active_time': time()})

    @tools.ormcache('sid')
    def _compute_session_token(self, sid):
        res = super(ResUsers, self)._compute_session_token(sid)
        if http.request:
            http.request.env.user._auth_timeout_check()
        return res

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        res = super(ResUsers, self).read(fields=fields, load=load)
        paths = self._auth_timeout_get_ignored_urls()
        if SUPERUSER_ID not in self.ids:
            path = http.request.httprequest.path if http.request else ''
            if path not in paths and path:
                session = self.env['ir.sessions'].search([('user_id', '=', self._uid), ('logged_in', '=', 'true')],
                                                         limit=1)
                if session:
                    session.last_active_time = time()
        return res