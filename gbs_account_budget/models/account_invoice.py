from odoo import models, fields, api, _
from odoo.exceptions import Warning

class AccountInvoice(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('price_subtotal_without_vat','operating_unit_id','account_analytic_id')
    def _onchange_subtotal_without_vat(self):
        if self.amount_untaxed:
            date = fields.Date.context_today(self)
            date_range_objs = self.env['date.range'].search(
                [('date_start', '<=', date),
                 ('date_end', '>=', date),
                 ('type_id.fiscal_year', '=', True),
                 ('active', '=', True)],
                order='id DESC', limit=1)
            bottom_budget_pool = self.env['bottom.line.budget'].search([
                ('fiscal_year', '=', date_range_objs.id),
                ('state','=','approve'),
                ('active','=',True)])
            bottom_line_budget_pool = self.env['bottom.line.budget.line'].search([
                ('bottom_line_budget', 'in', bottom_budget_pool.ids),
                ('bottom_line_account_id','=',self.account_id.id)],
                order='id DESC', limit=1)


            vals = [('budget_distribution_id.bottom_line_budget_line','=', bottom_line_budget_pool.id),
                    ('budget_distribution_id.state','=','approve')]

            if self.operating_unit_id:
                vals.append(('operating_unit_id','=',self.operating_unit_id.id))

            if self.account_analytic_id:
                vals.append(('analytic_account_id', '=', self.account_analytic_id.id))

            budget_distribution_line_pool = self.env['budget.distribution.line'].search(vals,order='id ASC')

            if len(budget_distribution_line_pool) > 1:
                budget_amount = sum([i.planned_amount - i.practical_amount for i in budget_distribution_line_pool])
            else:
                budget_amount = budget_distribution_line_pool.planned_amount - budget_distribution_line_pool.practical_amount

            if self.account_id and bottom_line_budget_pool and \
                            self.price_subtotal_without_vat > bottom_line_budget_pool.planned_amount:
                msg = 'The amount for ' + self.name + ' is crossed planned amount for GL budget.'
            elif self.operating_unit_id and self.account_analytic_id and budget_distribution_line_pool and \
                            self.price_subtotal_without_vat > budget_amount:
                msg = 'The amount for ' + self.name + ' is crossed planned amount for branch wise budget and cost centre wise budget.'
            elif self.operating_unit_id and budget_distribution_line_pool and \
                            self.price_subtotal_without_vat > budget_amount:
                msg = 'The amount for '+self.name+' is crossed planned amount for branch wise budget.'
            else:
                msg = False

            if msg:
                warning_mess = {
                    'title': _('Cross the budget!'),
                    'message': _(msg)
                }
                return {'warning': warning_mess}

            return {}
