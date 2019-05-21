from odoo import models, fields, api, _
from odoo.exceptions import Warning

class AccountInvoice(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('price_subtotal_without_vat')
    def _onchange_subtotal_without_vat(self):
        if self.price_subtotal_without_vat:
            gl_budget_pool = self.env['bottom.line.budget.line'].search([('bottom_line_account_id','=',self.account_id.id),('state','=','approve')])
            branch_budget_pool = self.env['branch.budget.line'].search([('branch_budget_id.account_id','=',self.account_id.id),
                                                                        ('operating_unit_id','=',self.operating_unit_id.id),('branch_budget_id.state','=','approve')])
            cost_budget_pool = self.env['cost.centre.budget.line'].search([('cost_centre_budget_id.account_id','=',self.account_id.id),
                                                                           ('analytic_account_id','=',self.account_analytic_id.id),('cost_centre_budget_id.state','=','approve')])

            if self.account_id and self.operating_unit_id and self.account_analytic_id and \
                gl_budget_pool and branch_budget_pool and cost_budget_pool and \
                self.price_subtotal_without_vat > gl_budget_pool.planned_amount and \
                self.price_subtotal_without_vat > branch_budget_pool.planned_amount and \
                self.price_subtotal_without_vat > cost_budget_pool.planned_amount:
                msg = 'The amount for ' + self.product_id.name + ' is crossed planned amount for GL budget and branch wise budget and cost centre wise budget.'
            elif self.account_id and self.price_subtotal_without_vat>gl_budget_pool.planned_amount:
                msg = 'The amount for '+self.product_id.name+' is crossed planned amount for GL budget.'
            elif self.operating_unit_id and branch_budget_pool and \
                    self.account_analytic_id and cost_budget_pool and \
                    self.price_subtotal_without_vat > branch_budget_pool.planned_amount and \
                    self.price_subtotal_without_vat > cost_budget_pool.planned_amount:
                msg = 'The amount for ' + self.product_id.name + ' is crossed planned amount for branch wise budget and cost centre wise budget.'
            elif self.operating_unit_id and branch_budget_pool and \
                    self.price_subtotal_without_vat>branch_budget_pool.planned_amount:
                msg = 'The amount for '+self.product_id.name+' is crossed planned amount for branch wise budget.'
            elif self.account_analytic_id and cost_budget_pool and \
                    self.price_subtotal_without_vat > cost_budget_pool.planned_amount:
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
