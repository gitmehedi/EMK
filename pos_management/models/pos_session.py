# -*- coding: utf-8 -*-

from odoo import models, api, fields,_
from odoo.addons.opa_utility.helper.utility import Message
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


class PosSession(models.Model):
    _name = "pos.session"
    _inherit = ['pos.session', 'mail.thread', 'ir.needaction_mixin']


    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['opening_control','opened','closing_control'])]


