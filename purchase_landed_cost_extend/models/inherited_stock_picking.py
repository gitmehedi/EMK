from odoo import fields, models, api, _


class InheritedStockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def name_get(self):
        display_mrr_no = self.env.context.get('display_mrr_no')
        result = []
        if display_mrr_no:
            for rec in self:
                if rec.check_mrr_button and rec.mrr_no:
                    name = rec.mrr_no
                    result.append((rec.id, name))
                else:
                    result.append((rec.id, ''))
        else:
            for rec in self:
                result.append((rec.id, rec.name))
        return result
