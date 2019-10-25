# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tools.translate import _
from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _query_get(self, domain=None):
        if domain is None:
            domain = []
        if self._context.get('ex_operating_unit_ids', False):
            domain.append(('operating_unit_id', 'not in',
                           self._context.get('ex_operating_unit_ids')))
        return super(AccountMoveLine, self)._query_get(domain)
