from odoo import fields,api,models,_

class FinalSettlement(models.Model):
    _name = "final.settlement"
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = 'Employee Exit Full & Final Settlement'

    employee_code = fields.Char('Employee Code',related='employee_id.employee_number',readonly=True)
    employee_id = fields.Many2one('hr.employee',string = 'Employee',required=True)
    emp_designation = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id',readonly=True, required=True)
    joining_date = fields.Date(related='employee_id.initial_employment_date', string='Date of Join', readonly=True)
    leaving_date = fields.Date(string='Date of Leaving',required=True)
    emp_payslip_ids = fields.One2many('final.settlement.line','final_settlement_id', string='Salary')
    payment_ids = fields.One2many('final.settlement.payments','payment_id', string='Salary')
    deduction_ids = fields.One2many('final.settlement.deduction','deduction_id', string='Salary')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('validate', 'Supervisor Approve'),
        ('approved', ' HR Approved'),
        ('done', ' Done'),
    ], string='Status', default='draft', track_visibility='onchange')

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.leaving_date = ''
        emp = self.env['hr.emp.exit.req'].search([('employee_id', '=', self.employee_id.id)], limit=1)
        if emp:
            self.leaving_date = emp.last_date
        else:
            pass

    @api.multi
    def action_submit(self):
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

class FinalSettlementLine(models.Model):
    _name = "final.settlement.line"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    total = fields.Float(string='Total')
    final_settlement_id = fields.Many2one('final.settlement','Final Settlement')

class Payments(models.Model):
    _name = "final.settlement.payments"

    name = fields.Char(string='Discription')
    amount = fields.Float(string='Amount')
    payment_id = fields.Many2one('final.settlement','Final Settlement')

class Diductions(models.Model):
    _name = "final.settlement.deduction"

    name = fields.Char(string='Discription')
    amount = fields.Float(string='Amount')
    deduction_id = fields.Many2one('final.settlement', 'Final Settlement')