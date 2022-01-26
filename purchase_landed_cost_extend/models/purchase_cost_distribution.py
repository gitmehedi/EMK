# import of python
import datetime

# import of odoo
from odoo import models, fields, api, _
from odoo.tools import frozendict


class PurchaseCostDistribution(models.Model):
    _inherit = 'purchase.cost.distribution'

    @api.multi
    def action_done(self):
        context = dict(self.env.context)
        context.update({
            'datetime_of_price_history': self.date + ' ' + datetime.datetime.now().strftime("%H:%M:%S"),
            'operating_unit_id': self.cost_lines[0].picking_id.operating_unit_id.id
        })
        self.env.context = frozendict(context)

        super(PurchaseCostDistribution, self).action_done()
