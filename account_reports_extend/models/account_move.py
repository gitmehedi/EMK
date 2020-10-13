
from odoo.tools.translate import _
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _query_get(self, domain=None):
        if domain is None:
            domain = []

        if not isinstance(domain, (list, tuple)):
            domain = safe_eval(domain)

        if self._context.get('cost_center_ids', False):
            domain.append(('cost_center_id', 'in', self._context.get('cost_center_ids').ids))

        if self._context.get('department_ids', False):
            domain.append(('department_id', 'in', self._context.get('department_ids').ids))

        return super(AccountMoveLine, self)._query_get(domain)

