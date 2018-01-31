from openerp import api, fields, models


class InheritedPosSession(models.Model):
    _inherit = 'pos.session'

    total_sell_value = fields.Float(string='Total Amount', digits=(16,2), compute='_compute_total')


    @api.depends('statement_ids')
    def _compute_total(self):

        for record in self:
            sum = 0
            if record.statement_ids:
                for rec in record.statement_ids:
                    sum = sum+ rec.balance_end

            record.total_sell_value = sum
