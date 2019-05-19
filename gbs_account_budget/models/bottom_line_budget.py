from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BottomLineBudget(models.Model):
    _name = "bottom.line.budget"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "name"
    _description = "Bottom Line Budget"

    name = fields.Char('Name',required=True, size=50, track_visibility='onchange',
                       readonly=True, states={'draft': [('readonly', False)]})
    date_create = fields.Datetime('Date', readonly=True, default=lambda self: fields.Datetime.now())
    bottom_line_budgets = fields.One2many('bottom.line.budget.line', 'bottom_line_budget',
                                          string='Bottom Lines',readonly=True, states={'draft': [('readonly', False)]})
    fiscal_year = fields.Many2one('date.range', string='Date range', track_visibility='onchange',
                                  domain="[('type_id.fiscal_year', '=', True)]",
                                  readonly=True, required=True, states={'draft': [('readonly', False)]})
    date_from = fields.Date(related='fiscal_year.date_start', string='Start Date', readonly=True)
    date_to = fields.Date(related='fiscal_year.date_end', string='End Date', readonly=True)
    confirm_date = fields.Datetime(string='Confirm Date', readonly=True, track_visibility='onchange')
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user)
    approved_user_id = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user)
    active = fields.Boolean(default=True,track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), '|',
                 ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning(_('[Unique Error] Name must be unique!'))

    @api.multi
    def action_budget_confirm(self):
        vals = {'state': 'confirm',
                'confirm_date': fields.Datetime.now(),
                }
        self.write(vals)
        self.bottom_line_budgets.write({'state': 'confirm'})

    @api.multi
    def action_budget_approve(self):
        vals = {'state': 'approve',
                'approve_date': fields.Datetime.now(),
                'approved_user_id': self.env.user.id
                }
        self.write(vals)
        self.bottom_line_budgets.write({'state': 'approve'})

    @api.multi
    def action_budget_draft(self):
        self.write({'state': 'draft'})
        self.bottom_line_budgets.write({'state': 'draft'})

    @api.multi
    def action_budget_cancel(self):
        self.write({'state': 'cancel'})
        self.bottom_line_budgets.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(BottomLineBudget, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]

    # @api.onchange('active')
    # def onchange_active(self):
    #     self.bottom_line_budgets.write({'active': self.active})

class BottomLineBudgetLine(models.Model):
    _name = "bottom.line.budget.line"
    _description = "Bottom Line Budget Line"

    bottom_line_budget = fields.Many2one('bottom.line.budget',string='Bottom line budget')
    bottom_line_account_id = fields.Many2one('account.account',string='Bottom Line Accounts',
                                             domain="[('internal_type', '!=', 'view')]",)
    planned_amount = fields.Float('Planned Amount', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    active = fields.Boolean(default=True,compute='_compute_active')

    def _compute_active(self):
        if self.bottom_line_budget and \
                        self.bottom_line_budget.active == False:
            self.active = False
        else:
            self.active = True

    @api.one
    @api.constrains('planned_amount')
    def _check_planned_amount(self):
        if self.planned_amount < 0:
            raise UserError('You can\'t give negative value!!!')

    @api.multi
    def action_branch_distribute(self):
        res = self.env.ref('gbs_account_budget.branch_budget_form')
        branch_budget_id = self.env['branch.budget'].search([('bottom_line_budget_line','=',self.id)])
        result = {'name': _('Branch Distribution'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'branch.budget',
                  'res_id': branch_budget_id.id or False,
                  'type': 'ir.actions.act_window',
                  'target': 'current',
                  'nodestroy': True,
                  'context': {'default_account_id': self.bottom_line_account_id.id,
                              'default_planned_amount': self.planned_amount,
                              'default_fiscal_year': self.bottom_line_budget.fiscal_year.id,
                              'default_name': self.bottom_line_budget.fiscal_year.name+'/'+self.bottom_line_account_id.name,
                              },
                  }

        return result

    @api.multi
    def action_cost_centre_distribute(self):
        res = self.env.ref('gbs_account_budget.cost_center_budget_form')
        cost_budget_id = self.env['cost.centre.budget'].search([('bottom_line_budget_line', '=', self.id)])
        result = {'name': _('Branch Distribution'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'cost.centre.budget',
                  'res_id': cost_budget_id.id or False,
                  'type': 'ir.actions.act_window',
                  'target': 'current',
                  'nodestroy': True,
                  'context': {'default_account_id': self.bottom_line_account_id.id,
                              'default_planned_amount': self.planned_amount,
                              'default_fiscal_year': self.bottom_line_budget.fiscal_year.id,
                              'default_name': self.bottom_line_budget.fiscal_year.name + '/' + self.bottom_line_account_id.name,
                              },
                  }

        return result
