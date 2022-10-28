from datetime import datetime, date, timedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class HrTedCafeBill(models.Model):
    _name = 'hr.ted.cafe.bill'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Ted Cafe Bills'
    _order = 'period_id desc'
    _rec_name = "period_id"

    def get_first_day(self):
        return datetime.today().replace(day=1)

    def get_last_day(self):
        next_month = date.today().replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    period_id = fields.Many2one("date.range", string="Select Period", readonly=True, required=True,
                                states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date', required=True, default=get_first_day, readonly=True, copy=True,
                            states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='End Date', required=True, default=get_last_day, readonly=True, copy=True,
                          states={'draft': [('readonly', False)]})
    total_amount = fields.Float(compute='_compute_total_amount', string='Total Amount')
    line_ids = fields.One2many(comodel_name='hr.ted.cafe.bill.line', inverse_name='line_id', string="Line Id",
                               readonly=True, copy=True, states={'confirm': [('readonly', False)]})
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm"), ('approve', "Approved"), ('done', "Done"), ],
                             default='draft')

    @api.multi
    @api.depends('line_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum([rec.amount for rec in record.line_ids])

    @api.multi
    def action_draft(self):
        if self.state == 'confirm':
            for line in self.line_ids:
                if line.state != 'adjusted':
                    line.write({'state': 'draft'})
            self.state = 'draft'

    @api.multi
    def act_gen_employee(self):
        if self.state == 'draft':
            employee = self.env['hr.employee'].sudo().search([('state', '=', 'employment')])
            line_empl = set([val.employee_id.id for val in self.line_ids])
            rest_empl = set(employee.ids) - line_empl
            for emp in rest_empl:
                self.line_ids.create({
                    'employee_id': emp,
                    'state': 'draft',
                    'date': fields.Date.today(),
                    'line_id': self.id,
                    'amount': 0,
                })
            self.state = 'confirm'

    @api.multi
    def action_confirm(self):
        if self.state == 'confirm':
            for line in self.line_ids:
                if line.state != 'adjusted':
                    line.write({'state': 'applied'})
            self.state = 'approve'

    @api.multi
    def action_done(self):
        if self.state == 'approve':
            for line in self.line_ids:
                if line.state != 'adjusted':
                    line.write({'state': 'approved'})
            self.state = 'done'

    @api.constrains('period_id')
    def _check_unique_constraint(self):
        if self.period_id:
            filters = [['period_id', '=', self.period_id.id]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Period must be unique!')

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('After Approval you can not delete this record.'))
            bill.line_ids.unlink()
        return super(HrTedCafeBill, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'approve')]


class HrTedCafeBillLine(models.Model):
    _name = 'hr.ted.cafe.bill.line'
    _description = 'HR Ted Cafe Bill Line'

    @api.model
    def _get_contract_employee(self):
        contracts = self.env['hr.contract'].search([('state', '=', 'open')])
        ids = [val.employee_id.id for val in contracts]
        return [('id', 'in', ids)]

    amount = fields.Float(string="Cafe Bill Amount", required=True, readonly=True,
                          states={'draft': [('readonly', False)]})
    date = fields.Date(string="Date", required=True, readonly=True, default=fields.Date.today,
                       states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True, required=True,
                                  domain=_get_contract_employee, readonly=True, states={'draft': [('readonly', False)]})
    line_id = fields.Many2one(comodel_name='hr.ted.cafe.bill', ondelete='cascade', string='Cafe No')

    state = fields.Selection([('draft', "Draft"),
                              ('applied', "Applied"),
                              ('approved', "Approved"),
                              ('adjusted', "Adjusted")
                              ], default='draft')


class InheritedHrTedCafePayslip(models.Model):
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.multi
    def action_payslip_done(self):
        res = super(InheritedHrTedCafePayslip, self).action_payslip_done()

        tcb_ids = []
        for li in self.input_line_ids:
            if li.code == 'TCB':
                tcb_ids.append(int(li.ref))

        tcb_data = self.env['hr.ted.cafe.bill.line'].browse(tcb_ids)
        tcb_data.write({'state': 'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedHrTedCafePayslip, self).onchange_employee()

            line_ids = self.input_line_ids
            lines = self.env['hr.ted.cafe.bill.line'].search([('employee_id', '=', self.employee_id.id),
                                                              ('state', '=', 'applied')])

            for line in lines:
                line_ids += line_ids.new({
                    'name': 'Ted Cafe Bill',
                    'code': "TCB",
                    'amount': line.amount,
                    'contract_id': self.contract_id.id,
                    'ref': line.id,
                })
            self.input_line_ids = line_ids
