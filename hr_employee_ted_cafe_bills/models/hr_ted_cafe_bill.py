from datetime import datetime, date, timedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class HrTedCafeBill(models.Model):
    _name = 'hr.ted.cafe.bill'
    _inherit = ['mail.thread']
    _description = 'Ted Cafe Bills'
    _order = 'name desc'

    def get_first_day(self):
        return datetime.today().replace(day=1)

    def get_last_day(self):
        next_month = date.today().replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    name = fields.Char(size=100, string="Name", required=True,
                       states={'draft': [('invisible', False)], 'applied': [('readonly', True)],
                               'approved': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date', required=True, default=get_first_day, readonly=True, copy=True,
                            states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='End Date', required=True, default=get_last_day, readonly=True, copy=True,
                          states={'draft': [('readonly', False)]})
    line_ids = fields.One2many(comodel_name='hr.ted.cafe.bill.line', inverse_name='parent_id', string="Line Id",
                               readonly=True, copy=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', "Draft"), ('approve', "Approved"), ('done', "Done"), ], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        for line in self.line_ids:
            if line.state != 'adjusted':
                line.write({'state': 'draft'})

    @api.multi
    def action_confirm(self):
        self.state = 'applied'
        for line in self.line_ids:
            if line.state != 'adjusted':
                line.write({'state': 'applied'})

    @api.multi
    def action_done(self):
        self.state = 'approved'
        for line in self.line_ids:
            if line.state != 'adjusted':
                line.write({'state': 'approved'})

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('After Approval you can not delete this record.'))
            bill.line_ids.unlink()
        return super(HrTedCafeBill, self).unlink()


class HrTedCafeBillLine(models.Model):
    _name = 'hr.ted.cafe.bill.line'
    _description = 'HR mobile bill line'

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
    parent_id = fields.Many2one(comodel_name='hr.ted.cafe.bill', ondelete='cascade', string='Cafe No')

    state = fields.Selection([('draft', "Draft"),
                              ('applied', "Applied"),
                              ('approved', "Approved"),
                              ('adjusted', "Adjusted")
                              ], default='draft')

