# imports of python
import datetime

# imports of odoo
from odoo import models, fields, api, _
from odoo.tools import frozendict


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def open_produce_product(self):
        self.ensure_one()
        action = super(MrpProduction, self).open_produce_product()
        action['context'] = {'operating_unit_id': self.operating_unit_id.id}
        return action

    @api.multi
    def button_mark_done(self):
        # Add operating unit in the context
        self._add_operating_unit_in_context(self.operating_unit_id.id)
        return super(MrpProduction, self).button_mark_done()

    @api.model
    def create(self, vals):
        # Add operating unit in the context
        self._add_operating_unit_in_context(vals.get('operating_unit_id') or self.env.user.default_operating_unit_id.id)
        if not vals.get('name', False) or vals['name'] == _('New'):
            requested_date = datetime.datetime.strptime(fields.Date.today(), "%Y-%m-%d").date()
            vals['name'] = self.env['ir.sequence'].next_by_code_new('mrp.production', requested_date)

        return super(MrpProduction, self).create(vals)

    @api.multi
    def write(self, vals):
        # Add operating unit in the context
        self._add_operating_unit_in_context(vals.get('operating_unit_id') or self.operating_unit_id.id)
        return super(MrpProduction, self).write(vals)

    def _add_operating_unit_in_context(self, operating_unit_id=False):
        """ Adding operating unit in context. """
        if operating_unit_id:
            context = dict(self.env.context)
            context.update({'operating_unit_id': operating_unit_id})
            self.env.context = frozendict(context)
