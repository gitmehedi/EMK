from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class OutstandingStatementWizard(models.TransientModel):
    _name = "outstanding.statement.wizard"

    executive_id = fields.Many2one('res.users', string='Executive')
    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    @api.onchange('executive_id')
    def _onchange_executive_id(self):
        user_ids = self.env['res.groups'].search([('name', '=', 'User: All Documents')]).users.ids

        return {'domain': {'executive_id': [('id', 'in', user_ids)]}}

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))
        elif (datetime.strptime(self.date_to, '%Y-%m-%d') - datetime.strptime(self.date_from, '%Y-%m-%d')).days > 365:
            raise ValidationError(_("Maximum date range is one year."))

    @api.multi
    def process_print(self):
        data = dict()
        data['executive_id'] = self.executive_id.id
        data['executive_name'] = self.executive_id.name
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to

        return self.env['report'].get_action(self, 'samuda_sales_report.report_outstanding_statement', data=data)
