from odoo import fields,api,models,_

class FinalSettlement(models.Model):
    _name = "final.settlement"
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = 'Employee Exit Full & Final Settlement'

    employee_code = fields.Char('Employee Code',related='employee_id.identification_id',readonly=True)
    employee_id = fields.Many2one('hr.employee',string = 'Employee',required=True, track_visibility='onchange')
    emp_designation = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id',readonly=True)
    joining_date = fields.Date(related='employee_id.initial_employment_date', string='Date of Join', readonly=True)
    leaving_date = fields.Date(string='Date of Leaving',readonly=True)
    emp_payslip_ids = fields.One2many('final.settlement.line','final_settlement_id', string='Salary')
    payment_ids = fields.One2many('final.settlement.payments','payment_id', string='Salary',track_visibility='onchange')
    deduction_ids = fields.One2many('final.settlement.deduction','deduction_id', string='Salary',track_visibility='onchange')
    payment_total_amount = fields.Float(string='Total Payment', readonly=True, compute='_compute_payment', store=True)
    deduction_total_amount = fields.Float(string='Total Deduction', readonly=True, compute='_compute_deduction', store=True)
    total_amount = fields.Float(string='Total', readonly=True, track_visibility='onchange', compute='_compute_total_amount', store=True)

    @api.multi
    @api.depends('payment_ids')
    def _compute_payment(self):
        self.payment_total_amount = 0.0
        for pay in self.payment_ids:
            self.payment_total_amount += pay.amount

    @api.multi
    @api.depends('deduction_ids')
    def _compute_deduction(self):
        self.deduction_total_amount = 0.0
        for deduc in self.deduction_ids:
            self.deduction_total_amount += deduc.amount

    @api.multi
    @api.depends('payment_ids', 'deduction_ids')
    def _compute_total_amount(self):
       self.total_amount = self.payment_total_amount - self.deduction_total_amount

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('approved', ' Approved'),
        ('done', ' Done'),
    ], string='Status', default='draft', track_visibility='onchange')

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.leaving_date = ''
        emp = self.env['hr.emp.exit.req'].search([('employee_id', '=', self.employee_id.id)], limit=1)
        if emp and emp.last_date:
            self.leaving_date = emp.last_date

    @api.model
    def create(self, vals):
        emp = self.env['hr.emp.exit.req'].search([('employee_id', '=', vals['employee_id'])], limit=1)
        if emp and emp.last_date:
            vals['leaving_date'] = emp.last_date
        res = super(FinalSettlement, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('employee_id'):
            emp = self.env['hr.emp.exit.req'].search([('employee_id', '=', vals['employee_id'])], limit=1)
            if emp and emp.last_date:
                vals['leaving_date'] = emp.last_date
            elif emp.last_date == False:
                vals['leaving_date'] = ''
        res = super(FinalSettlement, self).write(vals)
        return res

    @api.multi
    def action_confirm(self):
        vals = []
        epm_slip = self.env['hr.payslip'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'done')],order='date_to DESC',limit=1)
        for fac in epm_slip.line_ids:
            if fac.code in ('BASIC','TCA','OAS','MEDA','HRAMN','GROSS'):
                vals.append((0, 0, {
                    'code': fac.code,
                    'name': fac.name,
                    'total': fac.total,
                }))
        self.emp_payslip_ids = vals
        self.state = 'validate'
        self.payment_ids.write({'state': 'validate'})
        self.deduction_ids.write({'state': 'validate'})
        self.emp_payslip_ids.write({'state': 'validate'})

    @api.multi
    def action_reset(self):
        self.state = 'draft'
        self.payment_ids.write({'state': 'draft'})
        self.deduction_ids.write({'state': 'draft'})
        self.emp_payslip_ids.write({'state': 'draft'})
        self.emp_payslip_ids = ''

    @api.multi
    def action_approved(self):
        self.state = 'approved'
        self.payment_ids.write({'state': 'approved'})
        self.deduction_ids.write({'state': 'approved'})
        self.emp_payslip_ids.write({'state': 'approved'})

    @api.multi
    def action_done(self):
        self.state = 'done'
        self.payment_ids.write({'state': 'done'})
        self.deduction_ids.write({'state': 'done'})
        self.emp_payslip_ids.write({'state': 'done'})

class FinalSettlementLine(models.Model):
    _name = "final.settlement.line"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    total = fields.Float(string='Total')
    final_settlement_id = fields.Many2one('final.settlement','Final Settlement')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('approved', ' Approved'),
        ('done', ' Done'),
    ], string='Status', default='draft', track_visibility='onchange')

class Payments(models.Model):
    _name = "final.settlement.payments"

    name = fields.Char(string='Discription')
    amount = fields.Float(string='Amount')
    payment_id = fields.Many2one('final.settlement','Final Settlement')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('approved', ' Approved'),
        ('done', ' Done'),
    ], string='Status', default='draft', track_visibility='onchange')

class Diductions(models.Model):
    _name = "final.settlement.deduction"

    name = fields.Char(string='Discription')
    amount = fields.Float(string='Amount')
    deduction_id = fields.Many2one('final.settlement', 'Final Settlement')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('approved', ' Approved'),
        ('done', ' Done'),
    ], string='Status', default='draft', track_visibility='onchange')