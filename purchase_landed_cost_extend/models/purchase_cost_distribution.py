# import of python
from datetime import datetime

# import of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import frozendict


class PurchaseCostDistribution(models.Model):
    _inherit = 'purchase.cost.distribution'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True, readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    field_readonly = fields.Boolean(string='Field Readonly')

    @api.multi
    def action_calculate(self):
        # validation
        if any(datetime.strptime(line.picking_id.date_done, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") > self.date for line in self.cost_lines):
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

        super(PurchaseCostDistribution, self).action_done()

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            operating_unit = self.env['operating.unit'].browse(vals.get('operating_unit_id'))
            vals['name'] = self.env['ir.sequence'].next_by_code_new('purchase.cost.distribution', self.date, operating_unit)
        if not vals.get('field_readonly', False):
            vals['field_readonly'] = True

        return super(PurchaseCostDistribution, self).create(vals)

    @api.constrains('date')
    def _check_date(self):
        if self.date > datetime.today().strftime("%Y-%m-%d"):
            raise ValidationError(_("Date cannot be greater than Current Date."))

    debit_account = fields.Many2one('account.account', 'Asset / Inventory GL', required=True)

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

    def get_move_line_vals(self, name, date, journal_id, account_id, operating_unit_id, analytic_account_id,
                           debit, credit,
                           company_id):
        return {
            'name': name,
            'date': date,
            'journal_id': journal_id,
            'account_id': account_id,
            'operating_unit_id': operating_unit_id,
            'analytic_account_id': analytic_account_id,
            'debit': debit,
            'credit': credit,
            # 'company_id': company_id,
        }

    def post_journal_entry(self):
        if not self.analytic_account:
            raise UserError('Analytic Account not found!')

        journal_id = self.env['account.journal'].sudo().search(
            [('code', '=', 'STJ'), ('company_id', '=', self.operating_unit_id.company_id.id)], limit=1)
        if not journal_id:
            raise UserError('Stock Journal not found!')
        lc_pad_account = self.env['ir.values'].get_default('account.config.settings', 'lc_pad_account')

        if not lc_pad_account:
            raise UserError(
                _(
                    "LC PAD Account not set. Please contact your system administrator for assistance."))

        move_lines = []

        expense_lines = self.env['purchase.cost.distribution.expense'].search([('distribution', '=', self.id)])
        ref = ''
        for expense in expense_lines:
            ref = expense.ref
            credit_entry = self.get_move_line_vals(expense.ref, datetime.now().date(), journal_id.id,
                                                   expense.account_id.id,
                                                   self.operating_unit_id.id,
                                                   self.analytic_account.id,
                                                   0,
                                                   expense.expense_amount,
                                                   self.operating_unit_id.company_id.id)
            move_lines.append((0, 0, credit_entry))

        credit_entry = self.get_move_line_vals(ref, datetime.now().date(), journal_id.id,
                                               lc_pad_account,
                                               self.operating_unit_id.id,
                                               self.analytic_account.id,
                                               0,
                                               self.total_purchase,
                                               self.operating_unit_id.company_id.id)
        move_lines.append((0, 0, credit_entry))

        debit_entry = self.get_move_line_vals(ref, datetime.now().date(), journal_id.id,
                                              self.debit_account.id,
                                              self.operating_unit_id.id,
                                              False,
                                              self.total_expense + self.total_purchase,
                                              0,
                                              self.operating_unit_id.company_id.id)

        move_lines.append((0, 0, debit_entry))

        vals = {
            'name': 'Total Landed Cost Charge to Inventory Dept By Acc Dept',
            'journal_id': journal_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            'date': datetime.now().date(),
            'company_id': self.operating_unit_id.company_id.id,
            'state': 'draft',
            'line_ids': move_lines,
            'narration': '',
            'ref': 'landed cost provision'
        }

        move = self.env['account.move'].create(vals)
        self.write({'account_move_id': move.id})

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


class PurchaseCostDistributionLine(models.Model):
    _inherit = 'purchase.cost.distribution.line'

    date_done = fields.Datetime(string='Date of Transfer', related='move_id.picking_id.date_done')
