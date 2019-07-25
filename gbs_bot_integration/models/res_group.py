from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResGroups(models.Model):
    _inherit = 'res.groups'

    code = fields.Char('Code')

    @api.constrains('code')
    def _check_unique_constrain(self):
        if self.code:
            filters_code = [['code', '=ilike', self.code]]
            code = self.search(filters_code)
            if len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')