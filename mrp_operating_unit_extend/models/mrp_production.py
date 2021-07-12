# imports of python
import datetime

# imports of odoo
from odoo import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == _('New'):
            requested_date = datetime.datetime.strptime(fields.Date.today(), "%Y-%m-%d").date()
            vals['name'] = self.env['ir.sequence'].next_by_code_new('mrp.production', requested_date)

        return super(MrpProduction, self).create(vals)
