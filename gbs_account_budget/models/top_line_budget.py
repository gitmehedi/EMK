from odoo import api, fields, models, _
from odoo.exceptions import UserError
# ---------------------------------------------------------
# Top Line Budgets
# ---------------------------------------------------------
class TopLineBudgetTemp(models.Model):
    _name = "top.line.budget.temp"
    _inherit = ['mail.thread']
    _order = "name"
    _description = "Top Line Budgetary Template"

    name = fields.Char('Name',required=True, size=50, track_visibility='onchange')
    date_create = fields.Datetime('Date', readonly=True, default=lambda self: fields.Datetime.now())
    account_ids = fields.Many2many('account.account', 'account_top_line_temp_rel', 'top_line_temp_id', 'account_id',
                                   'Accounts',domain=[('user_type_id', '=', 'View Type')])


class TopLineBudget(models.Model):
    _name = "top.line.budget"
    _description = "Top Line Budget"
    _inherit = ['mail.thread']

    name = fields.Char('Budget Name', required=True,readonly=True,
                       states={'draft': [('readonly', False)]},track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible',readonly=True,track_visibility='onchange',
                                       default=lambda self: self.env.user)
    fiscal_year = fields.Many2one('date.range', string='Date range',track_visibility='onchange',
                                  readonly=True,required=True,states={'draft': [('readonly', False)]})
    date_from = fields.Date(related='fiscal_year.date_start',string='Start Date',readonly=True)
    date_to = fields.Date(related='fiscal_year.date_end',string='End Date',readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    top_line_budgets = fields.One2many('top.line.budget.lines', 'top_line_budget_id', 'Top Line Budget Lines',
                                       states={'draft': [('readonly', False)]}, copy=True)
    top_line_budget_temp_id = fields.Many2one('top.line.budget.temp', 'Top Line Budgetary', required=True,readonly=True,
                                              states={'draft': [('readonly', False)]})
    prepare_date = fields.Datetime(string='Prepare Date', readonly=True, track_visibility='onchange')
    confirm_date = fields.Datetime(string='Confirm Date', readonly=True, track_visibility='onchange')
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount', required=True,track_visibility='onchange',readonly=True,
                                  states={'draft': [('readonly', False)]})
    # practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount', track_visibility='onchange')
    # theoritical_amount = fields.Float(compute='_compute_theoritical_amount', string='Theoretical Amount', track_visibility='onchange')

    @api.onchange('top_line_budget_temp_id')
    def onchange_top_line_budget_temp(self):
        if self.top_line_budget_temp_id:
            self.top_line_budgets = []
            vals = []
            account_ids_pool = self.top_line_budget_temp_id.account_ids
            for obj in account_ids_pool:
                vals.append((0, 0, {'account_id': obj.id,
                                    'name': self.name+'/ '+obj.name,
                                    'fiscal_year': self.fiscal_year or False,
                                    }))
            self.top_line_budgets = vals


    @api.multi
    def action_budget_confirm(self):
        self.write({'state': 'confirm','confirm_date':fields.Datetime.now()})

    @api.multi
    def action_budget_validate(self):
        self.write({'state': 'validate', 'approve_date': fields.Datetime.now()})

    @api.multi
    def action_budget_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(TopLineBudget, self).unlink()


class TopLineBudgetLines(models.Model):
    _name = "top.line.budget.lines"
    _description = "Top Line Budget Line"

    name = fields.Char('Budget Name')
    top_line_budget_id = fields.Many2one('top.line.budget', 'Budget', ondelete='cascade', index=True, required=True)
    account_id = fields.Many2one('account.account', string='Accounts', domain=[('user_type_id', '=', 'View Type')])
    fiscal_year = fields.Many2one('date.range', string='Period',required=True)
    date_from = fields.Date(related='fiscal_year.date_start', string='Start Date', readonly=True)
    date_to = fields.Date(related='fiscal_year.date_end', string='End Date', readonly=True)
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount', store=True)
    theoritical_amount = fields.Float(string='Theoretical Amount',store=True)
    # theoritical_amount = fields.Float(compute='_compute_theoritical_amount', string='Theoretical Amount',store=True)
    #     practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount',store=True)
    #     analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',required=True)
    #     percentage = fields.Float(compute='_compute_percentage', string='Achievement')
    #     company_id = fields.Many2one(related='crossovered_budget_id.company_id', comodel_name='res.company',
    #         string='Company', store=True, readonly=True)
    #
    # @api.one
    # def name_get(self):
    #     name = self.name
    #     if self.account_id and self.fiscal_year:
    #         name = '[%s] %s' % (self.fiscal_year.name,self.account_id.name)
    #     return (self.id, name)
    # @api.multi
    # def _compute_practical_amount(self):
    #     for line in self:
    #         result = 0.0
    #         acc_ids = line.general_budget_id.account_ids.ids
    #         if not acc_ids:
    #             raise UserError(_("The Budget '%s' has no accounts!") % ustr(line.general_budget_id.name))
    #         date_to = self.env.context.get('wizard_date_to') or line.date_to
    #         date_from = self.env.context.get('wizard_date_from') or line.date_from
    #         if line.analytic_account_id.id:
    #             self.env.cr.execute("""
    #                 SELECT SUM(amount)
    #                 FROM account_analytic_line
    #                 WHERE account_id=%s
    #                     AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
    #                     AND general_account_id=ANY(%s)""",
    #             (line.analytic_account_id.id, date_from, date_to, acc_ids,))
    #             result = self.env.cr.fetchone()[0] or 0.0
    #         line.practical_amount = result

    # @api.multi
    # @api.depends('planned_amount')
    # def _compute_theoritical_amount(self):
    #     today = fields.Datetime.now()
    #     theo_amt = 0.00
    #     for line in self:
    #         # Used for the report
    #         if line.planned_amount and line.date_from and line.date_to:
    #             date_from = line.date_from
    #             date_to = line.date_to
    #             if date_from < fields.Datetime.from_string(line.date_from):
    #                 date_from = fields.Datetime.from_string(line.date_from)
    #             elif date_from > fields.Datetime.from_string(line.date_to):
    #                 date_from = False
    #
    #             if date_to > fields.Datetime.from_string(line.date_to):
    #                 date_to = fields.Datetime.from_string(line.date_to)
    #             elif date_to < fields.Datetime.from_string(line.date_from):
    #                 date_to = False
    #
    #             # theo_amt = 0.00
    #             if date_from and date_to:
    #                 line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(line.date_from)
    #                 elapsed_timedelta = date_to - date_from
    #                 if elapsed_timedelta.days > 0:
    #                     theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
    #         else:
    #             if line.paid_date:
    #                 if fields.Datetime.from_string(line.date_to) <= fields.Datetime.from_string(line.paid_date):
    #                     theo_amt = 0.00
    #                 else:
    #                     theo_amt = line.planned_amount
    #             else:
    #                 line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(line.date_from)
    #                 elapsed_timedelta = fields.Datetime.from_string(today) - (fields.Datetime.from_string(line.date_from))
    #
    #                 if elapsed_timedelta.days < 0:
    #                     # If the budget line has not started yet, theoretical amount should be zero
    #                     theo_amt = 0.00
    #                 elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(line.date_to):
    #                     # If today is between the budget line date_from and date_to
    #                     theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
    #                 else:
    #                     theo_amt = line.planned_amount
    #
    #         line.theoritical_amount = theo_amt