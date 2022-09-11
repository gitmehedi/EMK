from datetime import datetime, date, timedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class HrTedCafeCreditSale(models.Model):
    _name = 'hr.ted.cafe.credit.sale'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Ted Cafe Credit Sale'
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
    line_ids = fields.One2many(comodel_name='hr.ted.cafe.credit.sale.line', inverse_name='line_id', string="Line Id",
                               readonly=True, copy=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', "Draft"), ('approve', "Approved"), ('done', "Done"), ], default='draft')

    @api.multi
    @api.depends('line_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum([rec.amount for rec in record.line_ids])

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
        return super(HrTedCafeCreditSale, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'approve')]


class HrTedCafeCreditSaleLine(models.Model):
    _name = 'hr.ted.cafe.credit.sale.line'
    _description = 'HR Ted Cafe Credit Sale Line'

    @api.model
    def _get_contract_employee(self):
        contracts = self.env['hr.contract'].search([('state', '=', 'open')])
        ids = [val.employee_id.id for val in contracts]
        return [('id', 'in', ids)]

    amount = fields.Float(string="Credit Amount", required=True, readonly=True,
                          states={'draft': [('readonly', False)]})
    date = fields.Date(string="Credit Date", required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True, required=True,
                                  domain=_get_contract_employee, readonly=True, states={'draft': [('readonly', False)]})
    line_id = fields.Many2one(comodel_name='hr.ted.cafe.credit.sale', ondelete='cascade', string='Credit Sale No')
    pos_id = fields.Many2one('pos.order', string='Order No', readonly=True, states={'draft': [('readonly', False)]})

    state = fields.Selection([('draft', "Draft"),
                              ('applied', "Applied"),
                              ('approved', "Approved"),
                              ('adjusted', "Adjusted")
                              ], default='draft')


class InheritedHrTedCafeCreditPayslip(models.Model):
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.multi
    def action_payslip_done(self):
        res = super(InheritedHrTedCafeCreditPayslip, self).action_payslip_done()

        tccs_ids = []
        for li in self.input_line_ids:
            if li.code == 'TCCS':
                tccs_ids.append(int(li.ref))

        tccs_data = self.env['hr.ted.cafe.credit.sale.line'].browse(tccs_ids)
        tccs_data.write({'state': 'adjusted'})

        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if self.employee_id:
            self.input_line_ids = 0
            super(InheritedHrTedCafeCreditPayslip, self).onchange_employee()

            line_ids = self.input_line_ids
            lines = self.env['hr.ted.cafe.credit.sale.line'].search([('employee_id', '=', self.employee_id.id),
                                                                     ('state', '=', 'applied')])

            for line in lines:
                line_ids += line_ids.new({
                    'name': 'Ted Cafe Credit Sales',
                    'code': "TCCS",
                    'amount': line.amount,
                    'contract_id': self.contract_id.id,
                    'ref': line.id,
                })
            self.input_line_ids = line_ids


class PoSOrder(models.Model):
    _inherit = 'pos.order'

    credit_sale_id = fields.Many2one('hr.ted.cafe.credit.sale.line')


class PoSOrderLine(models.Model):
    _inherit = 'pos.order.line'

    tax_ids_after_fiscal_position = fields.Many2many(string='VAT')
