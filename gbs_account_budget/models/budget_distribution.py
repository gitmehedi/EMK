from datetime import timedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError,Warning, ValidationError

# ---------------------------------------------------------
# Budgets Distribution
# ---------------------------------------------------------
class BranchDistribution(models.Model):
    _name = "budget.distribution"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _description = "Budget Distribution"

    name = fields.Char('Budget Name',readonly=True, track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user.id)
    approved_user_id = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account', required=True,readonly=True,
                                 default=lambda self: self.env.context.get('default_account_id'),
                                 track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount',default=lambda self: self.env.context.get('default_planned_amount'),
                                  readonly=True,track_visibility='onchange')
    remaining_amount = fields.Float('Remaining Planned Amount',readonly=True,
                                    compute='_compute_remaining_amount',store=True)
    total_practical_amount = fields.Float('Total Practical Amount',readonly=True,
                                          compute='_compute_total_practical_amount',
                                          help='Sum of Practical Amount')
    rem_exceed_amount = fields.Float('Remaining/Exceed Amount', readonly=True,
                                     compute='_compute_rem_exceed_amount',
                                     help='Subtractions of Practical Amount and Planned Amount')
    fiscal_year = fields.Many2one('date.range', string='Date range', track_visibility='onchange',
                                  default=lambda self: self.env.context.get('default_fiscal_year'),
                                  readonly=True, required=True)
    date_from = fields.Date(related='fiscal_year.date_start', string='Start Date', readonly=True)
    date_to = fields.Date(related='fiscal_year.date_end', string='End Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('approve', 'Approved'),
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    budget_distribution_lines = fields.One2many('budget.distribution.line', 'budget_distribution_id',readonly=True,
                                                states={'draft': [('readonly', False)]},
                                                string='Lines')
    budget_distribution_history_ids = fields.One2many('budget.distribution.history', 'budget_distribution_id', readonly=True,
                                                      string='History Lines')
    bottom_line_budget_line = fields.Many2one('bottom.line.budget.line',
                                              string='Bottom line budget',
                                              default=lambda self: self.env.context.get('active_id'))
    active = fields.Boolean(default=True, track_visibility='onchange',compute='_compute_active')

    @api.multi
    def action_budget_approve(self):
        if self.env.user.id == self.creating_user_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        if self.state == 'draft':
            vals = {'state': 'approve',
                    'approve_date': fields.Datetime.now(),
                    'approved_user_id': self.env.user.id
                    }
            self.write(vals)

    @api.multi
    def action_budget_draft(self):
        if self.state == 'cancel':
            self.write({'state': 'draft'})

    @api.multi
    def action_budget_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(BranchDistribution, self).unlink()


    @api.multi
    @api.depends('planned_amount','budget_distribution_lines.planned_amount')
    def _compute_remaining_amount(self):
        for budget in self:
            if budget.planned_amount:
                distribution_line_total_amount = sum(line.planned_amount for line in budget.budget_distribution_lines)
                budget.remaining_amount = round(budget.planned_amount) - (round(distribution_line_total_amount))
            else:
                budget.remaining_amount = 0

    @api.constrains('remaining_amount')
    def _check_amount(self):
        self.ensure_one()
        if round(self.remaining_amount)>0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is still remaining.'% self.remaining_amount))
        elif round(self.remaining_amount)<0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is bigger then planned amount.'% -(self.remaining_amount)))
        return True

    def action_amendment(self):
        history_pools = self.env['budget.distribution.history']
        history_line_pools = self.env['budget.distribution.history.line']
        res = {
            'name': self.name,
            'creating_user_id': self.creating_user_id.id,
            'approved_user_id': self.approved_user_id.id,
            'account_id': self.account_id.id,
            'planned_amount': self.planned_amount,
            'remaining_amount': self.remaining_amount,
            'fiscal_year': self.fiscal_year.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'approve_date': self.approve_date,
            'budget_distribution_id': self.id,
            'bottom_line_budget_id': self.bottom_line_budget_line.id,
            'active': self.active,
        }
        history = history_pools.create(res)
        if history:
            history_id = history.id

        for line in self.budget_distribution_lines:
            lines = {
                'budget_distribution_history_id': history_id,
                'operating_unit_id': line.operating_unit_id.id,
                'analytic_account_id': line.analytic_account_id and line.analytic_account_id.id or False,
                'planned_amount': line.planned_amount,
                'practical_amount': line.practical_amount,
                'theoritical_amount': line.practical_amount,
                'active': self.active,
            }
            history_line_pools.create(lines)

        self.write({'state': 'draft','creating_user_id':self.env.user.id})

    def _compute_active(self):
        if self.bottom_line_budget_line and self.bottom_line_budget_line.active ==False:
            self.active = False
        else:
            self.active = True

    @api.one
    @api.depends('budget_distribution_lines.practical_amount')
    def _compute_total_practical_amount(self):
        for rec in self:
            rec.total_practical_amount = sum(line.practical_amount for line in rec.budget_distribution_lines)

    @api.one
    @api.depends('total_practical_amount', 'planned_amount')
    def _compute_rem_exceed_amount(self):
        for rec in self:
            rec.rem_exceed_amount = rec.planned_amount - rec.total_practical_amount

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]


        # def import_file(self, cr, uid, imp_id, context=None):
        #     """ Will do an asynchronous load of a CSV file.
        #
        #     Will generate an success/failure report and generate some
        #     maile threads. It uses BaseModel.load to lookup CSV.
        #     If you set bypass_orm to True then the load function
        #     will use a totally overridden create function that is a lot faster
        #     but that totally bypass the ORM
        #
        #     """
        #
        #     if isinstance(imp_id, list):
        #         imp_id = imp_id[0]
        #     if context is None:
        #         context = {}
        #     current = self.read(cr, uid, imp_id, ['bypass_orm', 'company_id'],
        #                         load='_classic_write')
        #     context['company_id'] = current['company_id']
        #     bypass_orm = current['bypass_orm']
        #     if bypass_orm:
        #         # Tells create funtion to bypass orm
        #         # As we bypass orm we ensure that
        #         # user is allowed to creat move / move line
        #         self._check_permissions(cr, uid, context=context)
        #         context['async_bypass_create'] = True
        #     head, data = self._parse_csv(cr, uid, imp_id)
        #     self.write(cr, uid, [imp_id], {'state': 'running',
        #                                    'report': _('Import is running')})
        #     self._allows_thread(imp_id)
        #     db_name = cr.dbname
        #     local_cr = pooler.get_db(db_name).cursor()
        #     thread = threading.Thread(target=self._load_data,
        #                               name='async_move_line_import_%s' % imp_id,
        #                               args=(local_cr, uid, imp_id, head, data),
        #                               kwargs={'context': context.copy()})
        #     thread.start()
        #
        #     return {}

# ---------------------------------------------------------
# Budgets Distribution Line
# ---------------------------------------------------------
class BudgetDistributionLine(models.Model):
    _name = "budget.distribution.line"
    _description = "Budget Distribution Line"

    budget_distribution_id = fields.Many2one('budget.distribution',string='Budget Distribution')
    operating_unit_id = fields.Many2one('operating.unit',required=True, string='Branch')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Centre', required=True)
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount',compute='_compute_practical_amount')
    remaining_amount = fields.Float(string='Remaining/Exceed Amount',compute='_compute_remaining_amount')
    theoritical_amount = fields.Float(string='Theoretical Amount' ,compute='_compute_theoritical_amount')
    active = fields.Boolean(default=True,compute='_compute_active')

    @api.one
    @api.constrains('operating_unit_id','analytic_account_id')
    def constrains_op_cost(self):
        if self.budget_distribution_id and self.operating_unit_id and self.analytic_account_id:
            domain = self.search(
                [('budget_distribution_id', '=', self.budget_distribution_id.id),
                 ('operating_unit_id', '=', self.operating_unit_id.id),
                 ('analytic_account_id', '=', self.analytic_account_id.id)])
            if len(domain) > 1:
                raise Warning(' Same branch and same cost centre can not be selected!')
        if self.budget_distribution_id and self.operating_unit_id:
            domain = self.search(
                [('budget_distribution_id', '=', self.budget_distribution_id.id),
                 ('operating_unit_id', '=', self.operating_unit_id.id),
                 ('analytic_account_id', '=', False)])
            if len(domain) > 1:
                raise Warning(' Same branch multiple time can not be selected!')


    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_id = line.budget_distribution_id.account_id.id
            date_to = line.budget_distribution_id.date_to
            date_from = line.budget_distribution_id.date_from
            acc_inv_ids = self.env['account.invoice'].search(
                [('date', '>=', date_from),
                 ('date', '<=', date_to),
                 ('state','!=','cancel')]).ids

            # where clause for operating unit wise and cost centre wise or just operating unit wise
            if line.operating_unit_id and line.analytic_account_id:
                where = ' AND operating_unit_id = '+str(line.operating_unit_id.id)+ \
                        ' AND account_analytic_id ='+str(line.analytic_account_id.id)
            else:
                where = ' AND operating_unit_id = '+str(line.operating_unit_id.id)+ \
                        ' AND account_analytic_id IS NULL'

            if acc_inv_ids:
                query = """
                    SELECT SUM(price_subtotal_without_vat)
                    FROM account_invoice_line
                    WHERE account_id=%s
                    AND invoice_id in %s
                    %s""" % (acc_id,(tuple(acc_inv_ids)),where)
                self.env.cr.execute(query)
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result


    @api.multi
    @api.depends('planned_amount')
    def _compute_theoritical_amount(self):
        today = fields.Datetime.now()
        theo_amt = 0.00
        for line in self:
            line_date_to = line.budget_distribution_id.date_to
            line_date_from = line.budget_distribution_id.date_from
            end_today = fields.Datetime.from_string(today) + timedelta(days=1)
            end_date_to = fields.Datetime.from_string(line_date_to) + timedelta(days=1)

            line_timedelta = end_date_to - fields.Datetime.from_string(line_date_from)
            elapsed_timedelta = end_today - fields.Datetime.from_string(line_date_from)

            if elapsed_timedelta.days < 0:
                # If the budget line has not started yet, theoretical amount should be zero
                theo_amt = 0.00
            elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(line_date_to):
                # If today is between the budget line date_from and date_to
                theo_amt = ((float(elapsed_timedelta.days) / float(line_timedelta.days))) * line.planned_amount
            else:
                theo_amt = line.planned_amount

            line.theoritical_amount = theo_amt

    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.planned_amount - rec.practical_amount


    def _compute_active(self):
        if self.budget_distribution_id and self.budget_distribution_id.active==False:
            self.active = False
        else:
            self.active = True

    @api.one
    @api.constrains('planned_amount')
    def _check_planned_amount(self):
        if self.planned_amount < 0:
            raise UserError('You can\'t give negative value!!!')

