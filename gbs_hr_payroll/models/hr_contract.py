from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class HrContract(models.Model):
    _name = 'hr.contract'
    _inherit = ['hr.contract','mail.thread', 'ir.needaction_mixin']

    transport_allowance = fields.Float(string='Trasport Allowance', digits=dp.get_precision('Payroll'),
                                       track_visibility='onchange', help='Amount for Transport Allowance')
    contractual = fields.Boolean(string="Contractual",track_visibility='onchange')

    name = fields.Char('Contract Reference', required=True,track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string="Department",track_visibility='onchange')
    type_id = fields.Many2one('hr.contract.type', string="Contract Type", required=True,track_visibility='onchange',
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    job_id = fields.Many2one('hr.job', string='Job Title',track_visibility='onchange')
    date_start = fields.Date('Start Date', required=True,track_visibility='onchange', default=fields.Date.today)
    date_end = fields.Date('End Date',track_visibility='onchange')
    trial_date_start = fields.Date('Trial Start Date',track_visibility='onchange')
    trial_date_end = fields.Date('Trial End Date',track_visibility='onchange')
    working_hours = fields.Many2one('resource.calendar', string='Working Schedule',track_visibility='onchange')
    wage = fields.Float('Wage', digits=(16, 2), required=True, help="Basic Salary of the employee",track_visibility='onchange')
    advantages = fields.Text('Advantages',track_visibility='onchange')
    notes = fields.Text('Notes',track_visibility='onchange')
    permit_no = fields.Char('Work Permit No',track_visibility='onchange')
    visa_no = fields.Char('Visa No',track_visibility='onchange')
    visa_expire = fields.Date('Visa Expire Date',track_visibility='onchange')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure',track_visibility='onchange')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',track_visibility='onchange')
    tds = fields.Float(string='TDS', digits=dp.get_precision('Payroll'),track_visibility='onchange',
                       help='Amount for Tax Deduction at Source')
    driver_salay = fields.Boolean(string='Driver Salary',track_visibility='onchange', help='Check this box if you provide allowance for driver')
    medical_insurance = fields.Float(string='Medical Insurance', digits=dp.get_precision('Payroll'),track_visibility='onchange',
                                     help='Deduction towards company provided medical insurance')
    voluntary_provident_fund = fields.Float(string='Voluntary Provident Fund (%)', digits=dp.get_precision('Payroll'),track_visibility='onchange',
                                            help='VPF is a safe option wherein you can contribute more than the PF ceiling of 12% that has been mandated by the government and VPF computed as percentage(%)')
    house_rent_allowance_metro_nonmetro = fields.Float(string='House Rent Allowance (%)',
                                                       digits=dp.get_precision('Payroll'),track_visibility='onchange',
                                                       help='HRA is an allowance given by the employer to the employee for taking care of his rental or accommodation expenses for metro city it is 50% and for non metro 40%. \nHRA computed as percentage(%)')
    supplementary_allowance = fields.Float(string='Supplementary Allowance',track_visibility='onchange', digits=dp.get_precision('Payroll'))

