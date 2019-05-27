from odoo import models, fields, api, _
from odoo.exceptions import Warning

class AccountInvoice(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('price_subtotal_without_vat','operating_unit_id','account_analytic_id')
    def _onchange_subtotal_without_vat(self):
        if self.price_subtotal_without_vat:
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
            branch_budget_pool = self.env['branch.budget.line'].search([
                ('branch_budget_id.bottom_line_budget_line', '=', bottom_line_budget_pool.id),
                ('operating_unit_id','=',self.operating_unit_id.id),
                ('branch_budget_id.state','=','approve')])
            cost_budget_pool = self.env['cost.centre.budget.line'].search([
                ('cost_centre_budget_id.bottom_line_budget_line', '=', bottom_line_budget_pool.id),
                ('analytic_account_id','=',self.account_analytic_id.id),
                ('cost_centre_budget_id.state','=','approve')])

            if self.account_id and self.operating_unit_id and self.account_analytic_id and \
                    bottom_line_budget_pool and branch_budget_pool and cost_budget_pool and \
                self.price_subtotal_without_vat > bottom_line_budget_pool.planned_amount and \
                self.price_subtotal_without_vat > branch_budget_pool.planned_amount-branch_budget_pool.practical_amount and \
                self.price_subtotal_without_vat > cost_budget_pool.planned_amount-cost_budget_pool.practical_amount:
                msg = 'The amount for ' + self.product_id.name + ' is crossed planned amount for GL budget and branch wise budget and cost centre wise budget.'
            elif self.account_id and bottom_line_budget_pool and \
                self.price_subtotal_without_vat>bottom_line_budget_pool.planned_amount:
                msg = 'The amount for '+self.product_id.name+' is crossed planned amount for GL budget.'
            elif self.operating_unit_id and branch_budget_pool and \
                    self.account_analytic_id and cost_budget_pool and \
                    self.price_subtotal_without_vat > branch_budget_pool.planned_amount-branch_budget_pool.practical_amount and \
                    self.price_subtotal_without_vat > cost_budget_pool.planned_amount-cost_budget_pool.practical_amount:
                msg = 'The amount for ' + self.product_id.name + ' is crossed planned amount for branch wise budget and cost centre wise budget.'
            elif self.operating_unit_id and branch_budget_pool and \
                    self.price_subtotal_without_vat>branch_budget_pool.planned_amount-branch_budget_pool.practical_amount:
                msg = 'The amount for '+self.product_id.name+' is crossed planned amount for branch wise budget.'
            elif self.account_analytic_id and cost_budget_pool and \
                    self.price_subtotal_without_vat > cost_budget_pool.planned_amount-cost_budget_pool.practical_amount:
                msg = 'The amount for '+self.product_id.name+' is crossed planned amount for cost centre wise budget.'
            else:
                msg = False

            if msg:
                warning_mess = {
                    'title': _('Cross the budget!'),
                    'message': _(msg)
                }
                return {'warning': warning_mess}

            return {}
