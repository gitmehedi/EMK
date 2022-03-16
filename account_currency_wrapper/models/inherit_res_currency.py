from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InheritCurrency(models.Model):
    _inherit = 'res.currency'

    rate = fields.Float(digits=(12, 8))
    reverse_rate = fields.Float(compute='_compute_current_reverse_rate', string='Current Rate', digits=(12, 8))

    @api.multi
    @api.depends('rate_ids.reverse_rate')
    def _compute_current_reverse_rate(self):
        date = self._context.get('date') or fields.Datetime.now()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        # the subquery selects the last rate before 'date' for the given currency/company
        query = """SELECT c.id, (SELECT r.reverse_rate FROM res_currency_rate r
                                      WHERE r.currency_id = c.id AND r.name <= %s
                                        AND (r.company_id IS NULL OR r.company_id = %s)
                                   ORDER BY r.company_id, r.name DESC
                                      LIMIT 1) AS rate
                       FROM res_currency c
                       WHERE c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.reverse_rate = currency_rates.get(currency.id) or 1.0
