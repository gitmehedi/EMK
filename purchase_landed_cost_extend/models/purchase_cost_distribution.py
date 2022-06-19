# import of python
from datetime import datetime

# import of odoo
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import frozendict
import openerp.addons.decimal_precision as dp

class PurchaseCostDistribution(models.Model):
    _name = "purchase.cost.distribution"
    _inherit = ["purchase.cost.distribution", "mail.thread"]

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True, readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    field_readonly = fields.Boolean(string='Field Readonly')

    @api.multi
    @api.depends('expense_lines', 'expense_lines.expense_amount')
    def _compute_total_expense(self):
        lc_pad_account = self.env['ir.values'].get_default('account.config.settings', 'lc_pad_account')
        for distribution in self:
            distribution.total_expense = sum([x.expense_amount for x in
                                              distribution.expense_lines.filtered(lambda x: x.account_id.id != lc_pad_account)])

    total_purchase = fields.Float(string='Total Product Cost')
    total_expense = fields.Float(
        compute=_compute_total_expense,
        digits=dp.get_precision('Account'), string='Total Landed Cost')

    lc_id = fields.Many2one("letter.credit", string='LC Number', readonly=True)

    @api.depends('cost_lines', 'cost_lines.total_amount','expense_lines', 'expense_lines.expense_amount')
    def _compute_lcost_per(self):
        for rec in self:
            if rec.cost_lines and rec.expense_lines:
                lc_pad_account = self.env['ir.values'].get_default('account.config.settings', 'lc_pad_account')
                total_purchase = sum([x.total_amount for x in rec.cost_lines])
                total_expense = sum([x.expense_amount for x in rec.expense_lines.filtered(lambda x: x.account_id.id != lc_pad_account)])
                if total_purchase != 0:
                    rec.percentage_of_lcost = (total_expense / (total_purchase+total_expense)) * 100
                else:
                    rec.percentage_of_lcost = False
            else:
                rec.percentage_of_lcost = False

    percentage_of_lcost = fields.Float(string='Landed Cost (%)', compute='_compute_lcost_per', store=False)

    @api.multi
    def action_calculate(self):
        # validation
        if any(datetime.strptime(line.picking_id.date_done, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") > self.date for
               line in self.cost_lines):
            raise ValidationError(_("Date cannot be less than the date of transfer of incoming shipments."))

        return super(PurchaseCostDistribution, self).action_calculate()

    @api.multi
    def action_done(self):
        context = dict(self.env.context)
        context.update({
            'datetime_of_price_history': self.date + ' ' + datetime.now().strftime("%H:%M:%S"),
            'operating_unit_id': self.cost_lines[0].picking_id.operating_unit_id.id
        })
        self.env.context = frozendict(context)

        self.ensure_one()
        if self.cost_update_type != 'direct':
            return
        d = {}
        for line in self.cost_lines:
            product = line.move_id.product_id
            if (product.cost_method != 'average' or
                    line.move_id.location_id.usage != 'supplier'):
                continue
            line.move_id.quant_ids._price_update(line.standard_price_new)
            d.setdefault(product, [])
            d[product].append(
                (line.move_id,
                 line.standard_price_new - line.standard_price_old, line.standard_price_new),
            )
        for product, vals_list in d.items():
            self._product_price_update(product, vals_list)
            for vals in vals_list:
                vals[0].product_price_update_after_done()
        self.state = 'done'

        #super(PurchaseCostDistribution, self).action_done()

    @api.multi
    def action_cancel(self):
        """Perform all moves that touch the same product in batch."""
        self.ensure_one()
        self.state = 'draft'
        if self.cost_update_type != 'direct':
            return
        d = {}
        for line in self.cost_lines:
            product = line.move_id.product_id
            if (product.cost_method != 'average' or
                    line.move_id.location_id.usage != 'supplier'):
                continue
            if self.currency_id.compare_amounts(
                    line.move_id.quant_ids[0].cost,
                    line.standard_price_new) != 0:
                raise exceptions.UserError(
                    _('Cost update cannot be undone because there has '
                      'been a later update. Restore correct price and try '
                      'again.'))
            line.move_id.quant_ids._price_update(line.standard_price_old)
            d.setdefault(product, [])
            d[product].append(
                (line.move_id,
                 line.standard_price_old - line.standard_price_new, line.standard_price_new),
            )
        for product, vals_list in d.items():
            self._product_price_update(product, vals_list)
            for vals in vals_list:
                vals[0].product_price_update_after_done()

    def _product_price_update(self, product, vals_list):
        """Method that mimicks stock.move's product_price_update_before_done
        method behaviour, but taking into account that calculations are made
        on an already done moves, and prices sources are given as parameters.
        """
        moves_total_qty = 0
        moves_total_diff_price = 0
        product_unit_cost = 0
        for move, price_diff, standard_price_new in vals_list:
            moves_total_qty += move.product_qty
            moves_total_diff_price += move.product_qty * price_diff
            product_unit_cost = standard_price_new
        prev_qty_available = product.qty_available - moves_total_qty
        if prev_qty_available <= 0:
            prev_qty_available = 0
        total_available = prev_qty_available + moves_total_qty

        include_product_purchase_cost = self.env['ir.values'].get_default('account.config.settings',
                                                                          'include_product_purchase_cost')

        ####################EDITED#####################

        if include_product_purchase_cost:
            new_std_price = ((product.standard_price * prev_qty_available) + (product_unit_cost * moves_total_qty)) / total_available
            self.message_post(
                body="%s : New Cost Price %s = ((Prev Cost Price %s *  Prev Qty %s) + (Total Cost Per Unit %s * New Qty %s)) / Qty(After Stock Update) %s" % (product.name,new_std_price, product.standard_price,prev_qty_available,product_unit_cost,moves_total_qty,total_available))
        else:
            new_std_price = ((total_available * product.standard_price + moves_total_diff_price) / total_available)
            self.message_post(
                body="%s : New Cost Price %s = ((Qty(After Stock Update) %s * Prev Cost Price %s + Total Landed Cost %s) /Qty(After Stock Update) %s)" % (product.name,new_std_price,total_available,product.standard_price,moves_total_diff_price,total_available))
        # Write the standard price, as SUPERUSER_ID, because a
        # warehouse manager may not have the right to write on products
        product.sudo().write({'standard_price': new_std_price})

    # override _prepare_expense_line to add account_id in return
    @api.model
    def _prepare_expense_line(self, expense_line, cost_line):
        res = super(PurchaseCostDistribution, self)._prepare_expense_line(expense_line, cost_line)
        res['account_id'] = expense_line.account_id.id
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            operating_unit = self.env['operating.unit'].browse(vals.get('operating_unit_id'))
            vals['name'] = self.env['ir.sequence'].next_by_code_new('purchase.cost.distribution', self.date,
                                                                    operating_unit)
        if not vals.get('field_readonly', False):
            vals['field_readonly'] = True

        return super(PurchaseCostDistribution, self).create(vals)

    @api.constrains('date')
    def _check_date(self):
        if self.date > datetime.today().strftime("%Y-%m-%d"):
            raise ValidationError(_("Date cannot be greater than Current Date."))

    debit_account = fields.Many2one('account.account', 'Asset / Inventory GL', readonly=True)

    analytic_account = fields.Many2one('account.analytic.account')
    account_move_id = fields.Many2one('account.move', readonly=True, string='Journal Entry')

    def action_import_using_analytic_account(self):
        return {
            'name': _('Select Analytic Account'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'analytic.account.selection.wizard',
            'target': 'new'
        }


    def post_journal_entry(self):
        return {
            'name': 'Post Journal Entry',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'journal.entry.post.wizard',
            'target': 'new',
        }

    def get_journal_entry(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', '=', self.account_move_id.id)],
            'context': "{'create': False}"
        }


    currency_rate = fields.Float('Currency Rate')

class PurchaseCostDistributionLine(models.Model):
    _inherit = 'purchase.cost.distribution.line'

    date_done = fields.Datetime(string='Date of Transfer', related='move_id.picking_id.date_done')

    cost_ratio = fields.Float(string="Landed Cost Per Unit")

    product_price_unit = fields.Float(string="Product Cost Per Unit")

    expense_amount = fields.Float(string='Landed Cost')

    total_amount = fields.Float(string='Product Cost')

    @api.depends('distribution')
    def compute_dist_state(self):
        for rec in self:
            if rec.distribution:
                rec.distribution_state = rec.distribution.state

    distribution_state = fields.Char(compute='compute_dist_state')
