from odoo import fields, models, api
import time


class CommissionRefundPercentageConfig(models.Model):
    _name = 'commission.refund.prcntg.config'
    _description = 'Commission Refund Percentage Configuration'

    name = fields.Char(default='/', readonly=True)
    type = fields.Selection([('monthly', 'Monthly'), ('yearly', 'Yearly')],
                            string='Type', required=True, default='monthly')

    @api.onchange('type')
    @api.model
    def get_domain_id(self):
        if self.type == 'monthly':
            return [('type_id.fiscal_month', '=', 'True')]
        elif self.type == 'yearly':
            return [('type_id.fiscal_year', '=', 'True')]

    fiscal_month = fields.Many2one('date.range', string='Fiscal Month/Year', required=True, domain=get_domain_id)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/' and vals['fiscal_month'] and vals['type']:
            date_range = self.env['date.range'].sudo().browse(vals['fiscal_month'])
            vals['name'] = vals['type'] + ': ' + date_range.name
        return super(CommissionRefundPercentageConfig, self).create(vals)

    @api.depends('fiscal_month')
    def compute_date(self):
        for rec in self:
            if rec.fiscal_month:
                rec.start_date = rec.fiscal_month.date_start
                rec.end_date = rec.fiscal_month.date_end

    start_date = fields.Date(compute='compute_date',store=True)
    end_date = fields.Date(compute='compute_date',store=True)

    company_id = fields.Many2one('res.company', string='Company')

    commission_line_ids = fields.One2many('commission.prcntg.config.line', 'parent_id')
    refund_line_ids = fields.One2many('refund.prcntg.config.line', 'parent_id')

    _sql_constraints = [
        ('type_fiscal_month_company',
         'unique(type,fiscal_month,company_id)',
         'A configuration already exist.'
         )
    ]

    @api.model
    def pull_automation_monthly(self):
        current_date = time.strftime("%d/%m/%Y")
        print('pull_automation_monthly')

    @api.model
    def pull_automation_yearly(self):
        current_date = time.strftime("%d/%m/%Y")
        print('pull_automation_yearly')


class CommissionPercentageConfigLine(models.Model):
    _name = 'commission.prcntg.config.line'

    parent_id = fields.Many2one('commission.refund.prcntg.config')
    from_range = fields.Float(string='From Range')
    to_range = fields.Float(string='To Range')
    rate = fields.Float(string='Rate(%)', size=3)


class RefundPercentageConfigLine(models.Model):
    _name = 'refund.prcntg.config.line'

    parent_id = fields.Many2one('commission.refund.prcntg.config')
    from_range = fields.Float(string='From Range')
    to_range = fields.Float(string='To Range')
    rate = fields.Float(string='Rate(%)', size=3)
