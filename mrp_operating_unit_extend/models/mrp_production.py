# imports of python
import datetime

# imports of odoo
from odoo import models, fields, api, _
from odoo.tools import frozendict


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('product_id', 'picking_type_id', 'company_id', 'operating_unit_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id,
                                                company_id=self.company_id.id,
                                                operating_unit_id=self.operating_unit_id.id)
            if bom.type == 'normal':
                self.bom_id = bom.id
            else:
                self.bom_id = False
            self.product_uom_id = self.product_id.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}

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
