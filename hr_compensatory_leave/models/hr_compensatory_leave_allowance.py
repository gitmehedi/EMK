from datetime import datetime, date, timedelta

from odoo import api
from odoo import models, fields, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class HrCompensatoryLeaveAllowance(models.Model):
    _name = 'hr.compensatory.leave.allowance'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Overtime Alllowance'
    _order = 'period_id desc'
    _rec_name = "period_id"

    def get_first_day(self):
        return datetime.today().replace(day=1)

    def get_last_day(self):
        next_month = date.today().replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    period_id = fields.Many2one('date.range', string="Period", required=True,
                                states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                                        'approved': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date', related='period_id.date_start', readonly=True, store=True)
    date_to = fields.Date(string='End Date', related='period_id.date_end', readonly=True, store=True)
    total_time = fields.Float(compute='_compute_total_time', string='Total Time')
    line_ids = fields.One2many(comodel_name='hr.compensatory.leave.allowance.line', inverse_name='line_id',
                               string="Line Id", readonly=True, copy=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', "Draft"), ('approve', "Approved"), ('done', "Done"), ], default='draft')

    @api.multi
    @api.depends('line_ids')
    def _compute_total_time(self):
        for record in self:
            record.total_time = sum([rec.hours for rec in record.line_ids])

    @api.multi
    def action_draft(self):
        if self.state == 'approve':
            for line in self.line_ids:
                if line.state != 'adjusted':
                    line.write({'state': 'draft'})
            self.state = 'draft'

    @api.multi
    def action_confirm(self):
        if self.state == 'draft':
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


    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.multi
    def action_gen_allowance(self):

        if self.state == 'draft':
            sql = """SELECT HE.ID,
                        SUM(HOR.TOTAL_HOURS) AS HOURS
                    FROM hr_ot_requisition HOR
                    LEFT JOIN hr_employee HE ON (HOR.EMPLOYEE_ID = HE.ID)
                    WHERE HOR.from_datetime BETWEEN %s AND %s
                        AND HOR.state='approved' AND HE.manager=false
                    GROUP BY HE.ID
                    ORDER BY HE.ID
            """

            self._cr.execute(sql, (self.date_from, self.date_to))  # Never remove the comma after the parameter
            allowance = self._cr.fetchall()
            self.line_ids.unlink()
            for line in allowance:
                rec = {'employee_id': line[0],
                       'hours': line[1],
                       'line_id': self.id,
                       'state': 'draft',
                       }
                self.line_ids.create(rec)

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('After Approval you can not delete this record.'))
            bill.line_ids.unlink()
        return super(HrCompensatoryLeaveAllowance, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'approve')]


class HrCompensatoryLeaveAllowanceLine(models.Model):
    _name = 'hr.compensatory.leave.allowance.line'
    _description = 'HR Compensatory Leave Allowance Line'

    @api.model
    def _get_contract_employee(self):
        contracts = self.env['hr.contract'].search([('state', '=', 'open')])
        ids = [val.employee_id.id for val in contracts]
        return [('id', 'in', ids)]

    hours = fields.Float(string="Allowance Hours", required=True, readonly=True,
                         states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True, required=True,
                                  domain=_get_contract_employee, readonly=True, states={'draft': [('readonly', False)]})
    line_id = fields.Many2one(comodel_name='hr.compensatory.leave.allowance', ondelete='cascade', string='Cafe No')

    state = fields.Selection([('draft', "Draft"),
                              ('applied', "Applied"),
                              ('approved', "Approved"),
                              ('adjusted', "Adjusted")
                              ], default='draft')


class InheritedCompensatoryLeavePayslip(models.Model):
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.multi
    def action_payslip_done(self):
        res = super(InheritedCompensatoryLeavePayslip, self).action_payslip_done()

        comleave_ids = []
        for li in self.input_line_ids:
            if li.code == 'COMLEAVE':
                comleave_ids.append(int(li.ref))

        comleave_data = self.env['hr.compensatory.leave.allowance.line'].browse(comleave_ids)
        comleave_data.write({'state': 'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedCompensatoryLeavePayslip, self).onchange_employee()

            line_ids = self.input_line_ids
            lines = self.env['hr.compensatory.leave.allowance.line'].search([('employee_id', '=', self.employee_id.id),
                                                                             ('state', '=', 'applied')])

            for line in lines:
                line_ids += line_ids.new({
                    'name': 'Compensatory Leave Allowance',
                    'code': "CLA",
                    'amount': line.amount,
                    'contract_id': self.contract_id.id,
                    'ref': line.id,
                })
            self.input_line_ids = line_ids
